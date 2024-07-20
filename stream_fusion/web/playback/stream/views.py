import redis
import asyncio
from functools import lru_cache
import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis.exceptions import LockError
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi_simple_rate_limiter import rate_limiter
from fastapi_simple_rate_limiter.database import create_redis_session

from stream_fusion.services.redis.redis_config import get_redis_cache_dependency
from stream_fusion.utils.cache.local_redis import RedisCache
from stream_fusion.logging_config import logger
from stream_fusion.settings import settings
from stream_fusion.utils.debrid.get_debrid_service import get_debrid_service
from stream_fusion.utils.parse_config import parse_config
from stream_fusion.utils.string_encoding import decodeb64
from stream_fusion.utils.security import check_api_key
from stream_fusion.constants import NO_CACHE_VIDEO_URL
from stream_fusion.web.playback.stream.schemas import (
    ErrorResponse,
    HeadResponse,
)


router = APIRouter()

redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port)
redis_session = create_redis_session(host=settings.redis_host, port=settings.redis_port)


@lru_cache(maxsize=128)
def get_adaptive_chunk_size(file_size):
    MB = 1024 * 1024
    GB = 1024 * MB

    if file_size < 1 * GB:
        chunk_size = 1 * MB
    elif file_size < 3 * GB:
        chunk_size = 2 * MB
    elif file_size < 9 * GB:
        chunk_size = 5 * MB
    elif file_size < 20 * GB:
        chunk_size = 10 * MB
    else:
        chunk_size = 20 * MB
    return chunk_size

async def proxy_stream(request: Request, url: str, headers: dict, max_retries: int = 3):
    logger.debug(f"Starting proxy_stream for URL: {url}")
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1} to get content from URL")
            async with request.app.state.http_session.get(url, headers=headers) as response:
                file_size = int(response.headers.get("Content-Length", 0))
                chunk_size = get_adaptive_chunk_size(file_size)

                async for chunk in response.content.iter_chunked(chunk_size): 
                    # iter_chunked is will return max size chunk, 
                    # but if chunk send by the server is less than chunk_size, 
                    # it will return that size.
                    yield chunk
                return
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"Connection error (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                logger.error("Max retries reached, raising exception")
                raise
            await asyncio.sleep(2**attempt)

    logger.error(f"Failed after {max_retries} attempts")
    raise Exception(f"Failed after {max_retries} attempts")

def get_stream_link(decoded_query: str, config: dict, ip: str, redis_cache: RedisCache) -> str:
    logger.debug(f"Getting stream link for query: {decoded_query}, IP: {ip}")
    cache_key = f"stream_link:{decoded_query}_{ip}"

    cached_link = redis_cache.get(cache_key)
    if cached_link:
        logger.info(f"Stream link found in cache: {cached_link}")
        return cached_link

    logger.debug("Stream link not found in cache, generating new link")
    debrid_service = get_debrid_service(config)
    link = debrid_service.get_stream_link(decoded_query, config, ip)

    if link != NO_CACHE_VIDEO_URL:
        logger.debug(f"Caching new stream link: {link}")
        redis_cache.set(cache_key, link, expiration=7200)  # Cache for 2 hour
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
):
    logger.debug(f"Received playback request for config: {config}, query: {query}")
    try:
        config = parse_config(config)
        api_key = config.get("apiKey")
        if not api_key:
            logger.warning("API key not found in config.")
            raise HTTPException(status_code=401, detail="API key not found in config.")

        await check_api_key(api_key)

        if not query:
            logger.warning("Query is empty")
            raise HTTPException(status_code=400, detail="Query required.")

        decoded_query = decodeb64(query)
        ip = request.client.host
        logger.debug(f"Decoded query: {decoded_query}, Client IP: {ip}")

        lock_key = f"lock:stream:{decoded_query}_{ip}"
        lock = redis_client.lock(lock_key, timeout=60)

        try:
            if lock.acquire(blocking=False):
                logger.debug("Lock acquired, getting stream link")
                link = get_stream_link(decoded_query, config, ip, redis_cache)
            else:
                logger.debug("Lock not acquired, waiting for cached link")
                cache_key = f"stream_link:{decoded_query}_{ip}"
                for _ in range(30):
                    await asyncio.sleep(1)
                    cached_link = redis_cache.get(cache_key)
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
                lock.release()
                logger.debug("Lock released")
            except LockError:
                logger.warning("Failed to release lock (already released)")

        if not settings.proxied_link:
            logger.debug(f"Redirecting to non-proxied link: {link}")
            return RedirectResponse(url=link, status_code=status.HTTP_301_MOVED_PERMANENTLY)

        logger.debug("Preparing to proxy stream")
        headers = {}
        range_header = request.headers.get("range")
        if range_header and "=" in range_header:
            logger.debug(f"Range header found: {range_header}")
            range_value = range_header.strip().split("=")[1]
            range_parts = range_value.split("-")

            start = int(range_parts[0]) if range_parts[0] else 0

            if len(range_parts) > 1 and range_parts[1]:
                end = int(range_parts[1])
                range_str = f"bytes={start}-{end}"
            else:
                range_str = f"bytes={start}-"

            headers["Range"] = range_str
            logger.debug(f"Range header set: {headers['Range']}")

        logger.debug(f"Initiating request to: {link}")
        async with request.app.state.http_session.get(link, headers=headers) as response:
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
                proxy_stream(request, link, headers, max_retries=3),
                status_code=response.status,
                headers=stream_headers,
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
):
    try:
        config = parse_config(config)
        api_key = config.get("apiKey")
        if api_key:
            await check_api_key(api_key)
        else:
            logger.warning("API key not found in config.")
            raise HTTPException(status_code=401, detail="API key not found in config.")

        if not query:
            raise HTTPException(status_code=400, detail="Query required.")
        decoded_query = decodeb64(query)
        ip = request.client.host
        cache_key = f"stream_link:{decoded_query}_{ip}"

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
            if redis_cache.exists(cache_key):
                link = redis_cache.get(cache_key)

                async with request.app.state.http_session.head(link) as response:
                    if response.status == 200:
                        headers["Content-Length"] = response.headers.get(
                            "Content-Length", "0"
                        )
                        return Response(status_code=status.HTTP_200_OK, headers=headers)

            await asyncio.sleep(1)

        return Response(status_code=status.HTTP_202_ACCEPTED, headers=headers)

    except Exception as e:
        logger.error(f"HEAD request error: {e}")
        return Response(
            status=500,
            content=ErrorResponse(
                detail="An error occurred while processing the request."
            ).model_dump_json(),
        )
