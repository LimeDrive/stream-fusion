import asyncio
from functools import lru_cache
import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi_simple_rate_limiter import rate_limiter
from fastapi_simple_rate_limiter.database import create_redis_session

from stream_fusion.constants import CustomException
from stream_fusion.services.redis.redis_config import get_redis_dependency
from stream_fusion.utils.cache.local_redis import RedisCache
from stream_fusion.logging_config import logger
from stream_fusion.settings import settings
from stream_fusion.utils.debrid.get_debrid_service import get_debrid_service
from stream_fusion.utils.parse_config import parse_config
from stream_fusion.utils.string_encoding import decodeb64
from stream_fusion.utils.security import check_api_key
from stream_fusion.web.playback.stream.schemas import (
    ErrorResponse,
    HeadResponse,
)


router = APIRouter()

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


async def proxy_stream(request: Request, url: str, headers: dict, proxy: str = None, max_retries: int = 3):
    """
    Stream content from the given URL with retry logic.
    """
    for attempt in range(max_retries):
        try:
            async with request.app.state.http_session.get(url, headers=headers, proxy=proxy) as response:
                file_size = int(response.headers.get("Content-Length", 0))
                chunk_size = get_adaptive_chunk_size(file_size)
                while True:
                    try:
                        chunk = await response.content.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
                    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                        logger.warning(f"Chunk read error (attempt {attempt + 1}): {str(e)}")
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

    redis_cache.set(cache_key, link, expiration=3600)  # Cache for 1 hour
    logger.info(f"Stream link generated and cached: {link}")

    return link


@router.get(
    "/{config}/{query}",
    responses={500: {"model": ErrorResponse}},
)
@rate_limiter(limit=1, seconds=2, redis=redis_session, exception=CustomException)
async def get_playback(
    config: str,
    query: str,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_dependency),
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

        link = get_stream_link(decoded_query, config, ip, redis_cache)

        range_header = request.headers.get("Range")
        headers = {}
        if range_header:
            headers["Range"] = range_header

        proxy = None  # Not yet implemented

        async with request.app.state.http_session.get(link, headers=headers, proxy=proxy) as response:
            if response.status == 206:
                return StreamingResponse(
                    proxy_stream(request, link, headers, proxy, max_retries=3),
                    status_code=206,
                    headers={
                        "Content-Range": response.headers["Content-Range"],
                        "Content-Length": response.headers["Content-Length"],
                        "Accept-Ranges": "bytes",
                        "Content-Type": "video/mp4",
                    },
                )
            elif response.status == 200:
                return StreamingResponse(
                    proxy_stream(request, link, headers, proxy, max_retries=3),
                    headers={
                        "Content-Type": "video/mp4",
                        "Accept-Ranges": "bytes",
                    },
                )
            else:
                return RedirectResponse(link, status_code=302)

    except Exception as e:
        logger.error(f"Playback error: {e}")
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
    redis_cache: RedisCache = Depends(get_redis_dependency),
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
