import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_simple_rate_limiter import rate_limiter
from redis import Redis
from tmdbv3api import TMDb, Find
from urllib.parse import quote_plus, urljoin

from stream_fusion.settings import settings
from stream_fusion.logging_config import logger
from stream_fusion.utils.yggfilx.yggflix_api import YggflixAPI
from stream_fusion.services.redis.redis_config import get_redis
from .schemas import RivenResponse, RivenResult, ErrorResponse, MediaTypes

router = APIRouter()

# Configuration TMDB API
tmdb = TMDb()
tmdb.api_key = settings.tmdb_api_key
tmdb.language = "fr-FR"
find = Find()


async def search_by_tmdb_id(
    yggflix: YggflixAPI, tmdb_id: int, type: str = "movie"
) -> List[dict]:
    """
    Search for torrents using a TMDB ID.

    Args:
        yggflix (YggflixAPI): Instance of YggflixAPI
        tmdb_id (int): TMDB ID to search for
        type (str): Media type ("movie" or "tv")

    Returns:
        List[dict]: List of torrent results
    """
    try:
        if type == MediaTypes.movie:
            return await asyncio.to_thread(yggflix.get_movie_torrents, tmdb_id)
        elif type == MediaTypes.tv:
            return await asyncio.to_thread(yggflix.get_tvshow_torrents, tmdb_id)
        return []
    except Exception as e:
        logger.error(f"Error searching by TMDB ID {tmdb_id}: {e}")
        return []


async def get_tmdb_id_from_imdb(imdb_id: str) -> Optional[str]:
    """
    Convert an IMDB ID to a TMDB ID.

    Args:
        imdb_id (str): IMDB ID to convert

    Returns:
        Optional[str]: TMDB ID if found, None otherwise
    """
    try:
        results = await asyncio.to_thread(find.find_by_imdb_id, imdb_id)
        if results.movie_results:
            return str(results.movie_results[0]["id"])
        elif results.tv_results:
            return str(results.tv_results[0]["id"])
        return None
    except Exception as e:
        logger.error(f"Error converting IMDB ID {imdb_id} to TMDB ID: {e}")
        return None


def __process_download_link(id: int, ygg_passkey) -> str:
    """Generate the download link for a given torrent."""
    if settings.yggflix_url:
        return f"https://yggapi.eu/torrent/{id}/download?passkey={ygg_passkey}"


def __process_magnet_link(
    ygg_passkey: str,
    info_hash: str,
    title: str = "unknown",
    announce_base: str = "http://connect.maxp2p.org:8080"
) -> str:
    """
    Generate a properly URL-encoded magnet link for a torrent.
    
    Args:
        ygg_passkey (str): User's YGG passkey for authentication
        info_hash (str): Torrent's info hash
        title (str, optional): Title of the torrent. Defaults to "unknown"
        announce_base (str, optional): Base announce URL. 
            Defaults to "http://connect.maxp2p.org:8080"
    
    Returns:
        str: Properly formatted and encoded magnet link
    
    Example:
        >>> process_magnet_link("abc123", "HASH123", "My Movie (2024)")
        'magnet:?xt=urn:btih:HASH123&dn=My+Movie+%282024%29&tr=http%3A%2F%2Fconnect.maxp2p.org%3A8080%2Fabc123%2Fannounce'
    """
    info_hash = info_hash.strip().lower()
    encoded_title = quote_plus(title)
    tracker_url = urljoin(announce_base.rstrip('/') + '/', f"{ygg_passkey}/announce")
    encoded_tracker = quote_plus(tracker_url)
    magnet_link = (
        f"magnet:?xt=urn:btih:{info_hash}"
        f"&dn={encoded_title}"
        f"&tr={encoded_tracker}"
    )
    return magnet_link

@router.get(
    "/yggflix",
    response_model=RivenResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
@rate_limiter(limit=20, seconds=60)
async def search_yggflix(
    type: MediaTypes = Query(
        MediaTypes.movie, description="Type of media (movie or tv)"
    ),
    ygg_passkey: str = Query(..., description="Ygg passkey"),
    query: Optional[str] = Query(None, description="Keyword search query"),
    tmdb_id: Optional[str] = Query(None, description="TMDB ID"),
    imdb_id: Optional[str] = Query(None, description="IMDB ID"),
    redis_client: Redis = Depends(get_redis),
) -> RivenResponse:
    """
    Search for torrents on Yggflix using various search parameters.

    Args:
        type (MediaTypes): Type of media to search for
        query (Optional[str]): Keyword search query
        tmdb_id (Optional[str]): TMDB ID
        imdb_id (Optional[str]): IMDB ID
        redis_client (Redis): Redis client for caching (future use)

    Returns:
        RivenResponse: Search results with metadata

    Raises:
        HTTPException: If the request is invalid or an error occurs
    """
    try:
        # Validate search parameters
        if not any([query, tmdb_id, imdb_id]):
            raise HTTPException(
                status_code=400,
                detail="At least one search parameter (query, tmdb_id, or imdb_id) must be provided",
            )

        yggflix = YggflixAPI()
        search_results = []
        final_tmdb_id = None
        final_imdb_id = imdb_id

        # IMDB ID search path
        if imdb_id:
            final_tmdb_id = await get_tmdb_id_from_imdb(imdb_id)
            if final_tmdb_id:
                search_results = await search_by_tmdb_id(
                    yggflix, int(final_tmdb_id), type
                )
            else:
                logger.warning(f"No TMDB ID found for IMDB ID: {imdb_id}")
                return RivenResponse(
                    query=imdb_id,
                    tmdb_id=None,
                    imdb_id=imdb_id,
                    total_results=0,
                    results=[],
                )

        # TMDB ID search path
        elif tmdb_id:
            final_tmdb_id = tmdb_id
            search_results = await search_by_tmdb_id(yggflix, int(tmdb_id), type)

        # Keyword search path
        else:
            search_results = await asyncio.to_thread(yggflix.get_torrents, q = query)

        # Process search results
        torrent_results = []
        for torrent in search_results:
            logger.debug(f"Processing torrent result: {torrent}")
            result = await asyncio.to_thread(yggflix.get_torrent_detail, torrent.get("id"))
            try:
                torrent_results.append(
                    RivenResult(
                        raw_title=result.get("title", "unknown"),
                        size=result.get("size"),
                        link=__process_download_link(
                            id=result.get("id"), ygg_passkey=ygg_passkey
                        ),
                        seeders=result.get("seeders"),
                        magnet=__process_magnet_link(
                            ygg_passkey=ygg_passkey,
                            info_hash=result.get("hash", "").lower(),
                            title=result.get("title", "unknown"),
                        ),
                        info_hash=result.get("hash", "").lower(),
                        privacy=result.get("privacy", "private"),
                        languages=result.get("languages", ["fr"]),
                        type=type,
                    )
                )
            except Exception as e:
                logger.error(f"Error processing torrent result: {e}")
                continue

        return RivenResponse(
            query=query or f"tmdbid:{final_tmdb_id}" or f"imdbid:{final_imdb_id}",
            tmdb_id=final_tmdb_id,
            imdb_id=final_imdb_id,
            total_results=len(torrent_results),
            results=torrent_results,
        )

    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the search request.",
        )
