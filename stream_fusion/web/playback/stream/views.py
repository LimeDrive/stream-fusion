import asyncio
from functools import lru_cache
import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse, StreamingResponse

from stream_fusion.services.redis.redis_config import get_redis_cache_dependency
from stream_fusion.utils.cache.local_redis import RedisCache
from stream_fusion.logging_config import logger
from stream_fusion.utils.debrid.get_debrid_service import get_debrid_service
from stream_fusion.utils.parse_config import parse_config
from stream_fusion.utils.string_encoding import decodeb64
from stream_fusion.web.playback.stream.schemas import (
    ErrorResponse,
    HeadResponse,
)


router = APIRouter()


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


async def proxy_stream(url: str, headers: dict, proxy: str = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, proxy=proxy) as response:
            file_size = int(response.headers.get("Content-Length", 0))
            chunk_size = get_adaptive_chunk_size(file_size)

            while True:
                chunk = await response.content.read(chunk_size)
                if not chunk:
                    break
                yield chunk


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
async def get_playback(
    config: str,
    query: str,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_cache_dependency),
):
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query required.")

        config = parse_config(config)
        decoded_query = decodeb64(query)
        ip = request.client.host

        link = get_stream_link(decoded_query, config, ip, redis_cache)

        range_header = request.headers.get("Range")
        headers = {}
        if range_header:
            headers["Range"] = range_header

        proxy = None  # Not yet implemented

        async with aiohttp.ClientSession() as session:
            async with session.get(link, headers=headers, proxy=proxy) as response:
                if response.status == 206:
                    return StreamingResponse(
                        proxy_stream(link, headers, proxy),
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
                        proxy_stream(link, headers, proxy),
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
    redis_cache: RedisCache = Depends(get_redis_cache_dependency),
):
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query required.")

        config = parse_config(config)
        decoded_query = decodeb64(query)
        ip = request.client.host

        cache_key = f"stream_link:{decoded_query}_{ip}"

        if redis_cache.exists(cache_key):
            return Response(status_code=status.HTTP_200_OK)
        else:
            await asyncio.sleep(0.2)
            return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"HEAD request error: {e}")
        return Response(
            status=500,
            content=ErrorResponse(
                detail="An error occurred while processing the request."
            ).model_dump_json(),
        )
