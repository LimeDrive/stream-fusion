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
        return 1 * MB  # 1 MB
    elif file_size < 3 * GB:
        return 2 * MB  # 2 MB
    elif file_size < 9 * GB:
        return 5 * MB  # 5 MB
    elif file_size < 20 * GB:
        return 10 * MB  # 10 MB
    else:
        return 20 * MB  # 20 MB


async def proxy_stream(
    request: Request, url: str, headers: dict, proxy: str = None, max_retries: int = 3
):
    """
    Stream content from the given URL with retry logic.
    """
    for attempt in range(max_retries):
        try:
            async with request.app.state.http_session.get(
                url, headers=headers, proxy=proxy
            ) as response:
                file_size = int(response.headers.get("Content-Length", 0))
                chunk_size = get_adaptive_chunk_size(file_size)
                while True:
                    try:
                        chunk = await response.content.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
                    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                        logger.warning(
                            f"Chunk read error (attempt {attempt + 1}): {str(e)}"
                        )
                        if attempt == max_retries - 1:
                            raise
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        break  # Exit the read loop to retry the connection
                else:
                    return  # Exit the function if everything went well
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"Connection error (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2**attempt)  # Exponential backoff

    raise Exception(f"Failed after {max_retries} attempts")


def get_stream_link(
    decoded_query: str, config: dict, ip: str, redis_cache: RedisCache
) -> str:
    cache_key = f"stream_link:{decoded_query}_{ip}"

    cached_link = redis_cache.get(cache_key)
    if cached_link:
        logger.info(f"Stream link cached: {cached_link}")
        return cached_link

    debrid_service = get_debrid_service(config)
    link = debrid_service.get_stream_link(decoded_query, config, ip)

    if link != NO_CACHE_VIDEO_URL:
        redis_cache.set(cache_key, link, expiration=3600)  # Cache for 1 hour
        logger.info(f"Stream link generated and cached: {link}")
    return link


@router.get(
    "/{config}/{query}",
    responses={500: {"model": ErrorResponse}},
)
@rate_limiter(limit=20, seconds=60, redis=redis_session)
async def get_playback(
    config: str,
    query: str,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_cache_dependency),
):
    try:
        config = parse_config(config)
        api_key = config.get("apiKey")
        if not api_key:
            logger.warning("API key not found in config.")
            raise HTTPException(status_code=401, detail="API key not found in config.")

        await check_api_key(api_key)

        if not query:
            raise HTTPException(status_code=400, detail="Query required.")

        decoded_query = decodeb64(query)
        ip = request.client.host

        lock_key = f"lock:stream:{decoded_query}_{ip}"
        lock = redis_client.lock(lock_key, timeout=60)

        try:
            if lock.acquire(blocking=False):
                link = get_stream_link(decoded_query, config, ip, redis_cache)
            else:
                cache_key = f"stream_link:{decoded_query}_{ip}"
                for _ in range(30):
                    await asyncio.sleep(1)
                    cached_link = redis_cache.get(cache_key)
                    if cached_link:
                        link = cached_link
                        break
                else:
                    raise HTTPException(
                        status_code=503,
                        detail="Service temporarily unavailable. Please try again.",
                    )
        finally:
            try:
                lock.release()
            except LockError:
                pass

        headers = {}
        range_header = request.headers.get("range")
        if range_header and "=" in range_header:
            range_value = range_header.strip().split("=")[1]
            range_parts = range_value.split("-")
            
            start = int(range_parts[0]) if range_parts[0] else 0
            
            if len(range_parts) > 1 and range_parts[1]:
                end = int(range_parts[1])
                range_str = f"bytes={start}-{end}"
            else:
                range_str = f"bytes={start}-"
            
            headers["Range"] = range_str

        proxy = None  # Not yet implemented

        async with request.app.state.http_session.get(
            link, headers=headers, proxy=proxy
        ) as response:
            stream_headers = {
                "Content-Type": "video/mp4",
                "Accept-Ranges": "bytes",
            }

            if response.status == 206:
                stream_headers["Content-Range"] = response.headers["Content-Range"]

            return StreamingResponse(
                proxy_stream(request, link, headers, proxy, max_retries=3),
                status_code=response.status,
                headers=stream_headers,
            )

    except Exception as e:
        logger.error(f"Playback error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail="An error occurred while processing the request."
            ).model_dump(),
        )


@router.head(
    "/{config}/{query}",
    response_model=HeadResponse,
    responses={500: {"model": ErrorResponse}},
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

        if redis_cache.exists(cache_key):
            return Response(status_code=status.HTTP_200_OK)
        else:
            await asyncio.sleep(0.4)
            return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"HEAD request error: {e}")
        return Response(
            status=500,
            content=ErrorResponse(
                detail="An error occurred while processing the request."
            ).model_dump_json(),
        )
