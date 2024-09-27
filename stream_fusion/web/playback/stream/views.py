import json
import redis.asyncio as redis
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis.exceptions import LockError
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi_simple_rate_limiter import rate_limiter
from fastapi_simple_rate_limiter.database import create_redis_session
from starlette.background import BackgroundTask

from stream_fusion.services.postgresql.dao.apikey_dao import APIKeyDAO
from stream_fusion.services.redis.redis_config import get_redis_cache_dependency
from stream_fusion.utils.cache.local_redis import RedisCache
from stream_fusion.logging_config import logger
from stream_fusion.settings import settings
from stream_fusion.utils.debrid.get_debrid_service import get_all_debrid_services, get_debrid_service
from stream_fusion.utils.parse_config import parse_config
from stream_fusion.utils.string_encoding import decodeb64
from stream_fusion.utils.security import check_api_key
from stream_fusion.constants import NO_CACHE_VIDEO_URL
from stream_fusion.web.playback.stream.schemas import (
    ErrorResponse,
    HeadResponse,
)


router = APIRouter()

redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
redis_session = create_redis_session(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)


class ProxyStreamer:
    def __init__(self, request: Request, url: str, headers: dict):
        self.request = request
        self.url = url
        self.headers = headers
        self.response = None

    async def stream_content(self):
        async with self.request.app.state.http_session.get(
            self.url, headers=self.headers
        ) as self.response:
            async for chunk in self.response.content.iter_any():
                yield chunk

    async def close(self):
        if self.response:
            await self.response.release()
        logger.debug("Streaming connection closed")


async def get_stream_link(
    decoded_query: str, config: dict, ip: str, redis_cache: RedisCache
) -> str:
    logger.debug(f"Getting stream link for query: {decoded_query}, IP: {ip}")
    api_key = config.get("apiKey")
    cache_key = f"stream_link:{api_key}:{decoded_query}_{ip}"

    cached_link = await redis_cache.get(cache_key)
    if cached_link:
        logger.info(f"Stream link found in cache: {cached_link}")
        return cached_link

    logger.debug("Stream link not found in cache, generating new link")

    query = json.loads(decoded_query)
    debrid = query.get("service", False)

    if debrid:
        debrid_service = get_debrid_service(config, debrid)
    
    link = debrid_service.get_stream_link(query, config, ip)

    if link != NO_CACHE_VIDEO_URL:
        logger.debug(f"Caching new stream link: {link}")
        await redis_cache.set(cache_key, link, expiration=7200)  # Cache for 2 hours
        logger.info(f"New stream link generated and cached: {link}")
    else:
        logger.debug("Stream link not cached (NO_CACHE_VIDEO_URL)")
    return link


@router.get("/{config}/{query}", responses={500: {"model": ErrorResponse}})
@rate_limiter(limit=20, seconds=60, redis=redis_session)
async def get_playback(
    config: str,
    query: str,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_cache_dependency),
    apikey_dao: APIKeyDAO = Depends()
):
    logger.debug(f"Received playback request for config: {config}, query: {query}")
    try:
        config = parse_config(config)
        api_key = config.get("apiKey")
        if not api_key:
            logger.warning("API key not found in config.")
            raise HTTPException(status_code=401, detail="API key not found in config.")

        await check_api_key(api_key, apikey_dao)

        if not query:
            logger.warning("Query is empty")
            raise HTTPException(status_code=400, detail="Query required.")

        decoded_query = decodeb64(query)
        ip = request.client.host
        logger.debug(f"Decoded query: {decoded_query}, Client IP: {ip}")

        lock_key = f"lock:stream:{api_key}:{decoded_query}_{ip}"
        lock = redis_client.lock(lock_key, timeout=60)

        try:
            if await lock.acquire(blocking=False):
                logger.debug("Lock acquired, getting stream link")
                link = await get_stream_link(decoded_query, config, ip, redis_cache)
            else:
                logger.debug("Lock not acquired, waiting for cached link")
                cache_key = f"stream_link:{api_key}:{decoded_query}_{ip}"
                for _ in range(30):
                    await asyncio.sleep(1)
                    cached_link = await redis_cache.get(cache_key)
                    if cached_link:
                        logger.debug("Cached link found while waiting")
                        link = cached_link
                        break
                else:
                    logger.warning("Timed out waiting for cached link")
                    raise HTTPException(
                        status_code=503,
                        detail="Service temporarily unavailable. Please try again.",
                    )
        finally:
            try:
                await lock.release()
                logger.debug("Lock released")
            except LockError:
                logger.warning("Failed to release lock (already released)")

        if not settings.proxied_link:
            logger.debug(f"Redirecting to non-proxied link: {link}")
            return RedirectResponse(
                url=link, status_code=status.HTTP_301_MOVED_PERMANENTLY
            )

        logger.debug("Preparing to proxy stream")
        headers = {}
        range_header = request.headers.get("range")
        if range_header and "=" in range_header:
            logger.debug(f"Range header found: {range_header}")
            range_value = range_header.strip().split("=")[1]
            range_parts = range_value.split("-")
            start = int(range_parts[0]) if range_parts[0] else 0
            end = int(range_parts[1]) if len(range_parts) > 1 and range_parts[1] else ""
            headers["Range"] = f"bytes={start}-{end}"
            logger.debug(f"Range header set: {headers['Range']}")

        streamer = ProxyStreamer(request, link, headers)

        logger.debug(f"Initiating request to: {link}")
        async with request.app.state.http_session.head(
            link, headers=headers
        ) as response:
            logger.debug(f"Response status: {response.status}")
            stream_headers = {
                "Content-Type": "video/mp4",
                "Accept-Ranges": "bytes",
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Connection": "keep-alive",
                "Content-Disposition": "inline",
                "Access-Control-Allow-Origin": "*",
            }

            if response.status == 206:
                logger.debug("Partial content response")
                stream_headers["Content-Range"] = response.headers["Content-Range"]

            for header in ["Content-Length", "ETag", "Last-Modified"]:
                if header in response.headers:
                    stream_headers[header] = response.headers[header]
                    logger.debug(f"Header set: {header}: {stream_headers[header]}")

            logger.debug("Preparing streaming response")
            return StreamingResponse(
                streamer.stream_content(),
                status_code=206 if "Range" in headers else 200,
                headers=stream_headers,
                background=BackgroundTask(streamer.close),
            )

    except Exception as e:
        logger.error(f"Playback error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail="An error occurred while processing the request."
            ).model_dump(),
        )


@router.head(
    "/{config}/{query}",
    response_model=HeadResponse,
    responses={500: {"model": ErrorResponse}, 202: {"model": None}},
)
async def head_playback(
    config: str,
    query: str,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_cache_dependency),
    apikey_dao: APIKeyDAO = Depends()
):
    try:
        config = parse_config(config)
        api_key = config.get("apiKey")
        if api_key:
            await check_api_key(api_key, apikey_dao)
        else:
            logger.warning("API key not found in config.")
            raise HTTPException(status_code=401, detail="API key not found in config.")

        if not query:
            raise HTTPException(status_code=400, detail="Query required.")
        decoded_query = decodeb64(query)
        ip = request.client.host
        cache_key = f"stream_link:{api_key}:{decoded_query}_{ip}"

        headers = {
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
        }

        for _ in range(30):
            if await redis_cache.exists(cache_key):
                link = await redis_cache.get(cache_key)

                if not settings.proxied_link:  # avoid sending HEAD request if link is sent directly
                    return Response(status_code=status.HTTP_200_OK, headers=headers)

                async with request.app.state.http_session.head(link) as response:
                    if response.status == 200:
                        headers["Content-Length"] = response.headers.get(
                            "Content-Length", "0"
                        )
                        return Response(status_code=status.HTTP_200_OK, headers=headers)

            await asyncio.sleep(1)

        return Response(status_code=status.HTTP_202_ACCEPTED, headers=headers)

    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"HEAD request error: {e}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                detail="An error occurred while processing the request."
            ).model_dump_json(),
            media_type="application/json"
        )