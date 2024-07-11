import hashlib
import time
from fastapi import APIRouter, Depends, HTTPException, Request

from stream_fusion.services.redis.redis_config import get_redis_dependency
from stream_fusion.utils.cache.cache import search_public
from stream_fusion.utils.cache.local_redis import RedisCache
from stream_fusion.logging_config import logger
from stream_fusion.utils.debrid.get_debrid_service import get_debrid_service
from stream_fusion.utils.filter_results import (
    filter_items,
    filter_out_non_matching_movies,
    filter_out_non_matching_series,
    merge_items,
    sort_items,
)
from stream_fusion.utils.jackett.jackett_result import JackettResult
from stream_fusion.utils.jackett.jackett_service import JackettService
from stream_fusion.utils.metdata.cinemeta import Cinemeta
from stream_fusion.utils.metdata.tmdb import TMDB
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.utils.parse_config import parse_config
from stream_fusion.utils.security.security_api_key import check_api_key
from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.web.root.search.schemas import SearchResponse, Stream
from stream_fusion.web.root.search.stremio_parser import parse_to_stremio_streams
from stream_fusion.utils.torrent.torrent_service import TorrentService
from stream_fusion.utils.torrent.torrent_smart_container import TorrentSmartContainer
from stream_fusion.utils.zilean.zilean_result import ZileanResult
from stream_fusion.utils.zilean.zilean_service import ZileanService
from stream_fusion.settings import settings


router = APIRouter()


@router.get("/{config}/stream/{stream_type}/{stream_id}", response_model=SearchResponse)
async def get_results(
    config: str,
    stream_type: str,
    stream_id: str,
    request: Request,
    redis_cache: RedisCache = Depends(get_redis_dependency),
) -> SearchResponse:
    start = time.time()
    logger.info(f"Stream request: {stream_type} - {stream_id}")

    stream_id = stream_id.replace(".json", "")
    config = parse_config(config)
    logger.debug(f"Parsed configuration: {config}")
    api_key = config.get("apiKey")
    if api_key:
        await check_api_key(api_key)
    else:
        logger.warning("API key not found in config.")
        raise HTTPException(status_code=401, detail="API key not found in config.")

    def get_metadata():
        logger.info(f"Fetching metadata from {config['metadataProvider']}")
        if config["metadataProvider"] == "tmdb" and settings.tmdb_api_key:
            metadata_provider = TMDB(config)
        else:
            metadata_provider = Cinemeta(config)
        return metadata_provider.get_metadata(stream_id, stream_type)

    media = redis_cache.get_or_set(
        get_metadata, stream_id, stream_type, config["metadataProvider"]
    )
    logger.info(f"Retrieved media metadata: {str(media.titles)}")

    def stream_cache_key(media):
        if isinstance(media, Movie):
            key_string = f"stream:{media.titles[0]}:{media.year}:{media.languages[0]}"
        elif isinstance(media, Series):
            key_string = f"stream:{media.titles[0]}:{media.languages[0]}:{media.season}{media.episode}"
        else:
            raise TypeError("Only Movie and Series are allowed as media!")
        hashed_key = hashlib.sha256(key_string.encode("utf-8")).hexdigest()
        return hashed_key[:16]

    cached_result = redis_cache.get(stream_cache_key(media))
    if cached_result is not None:
        logger.info("Returning cached processed results")
        total_time = time.time() - start
        logger.info(f"Request completed in {total_time:.2f} seconds")
        return SearchResponse(streams=cached_result)

    debrid_service = get_debrid_service(config)

    def filter_all_results(results, media):
        if media.type == "series":
            filtered = filter_out_non_matching_series(
                results, media.season, media.episode
            )
            logger.info(
                f"Filtered series results: {len(filtered)} (from {len(results)})"
            )
            return filtered
        else:
            filtered = filter_out_non_matching_movies(results, media.year)
            logger.info(
                f"Filtered movie results: {len(filtered)} (from {len(results)})"
            )
        return results
    
    def media_cache_key(media):
        if isinstance(media, Movie):
            key_string = f"media:{media.titles[0]}:{media.year}:{media.languages[0]}"
        elif isinstance(media, Series):
            key_string = f"media:{media.titles[0]}:{media.languages[0]}:{media.season}"
        else:
            raise TypeError("Only Movie and Series are allowed as media!")
        hashed_key = hashlib.sha256(key_string.encode("utf-8")).hexdigest()
        return hashed_key[:16]

    def get_search_results(media, config):
        search_results = []
        torrent_service = TorrentService()

        def perform_search(update_cache=False):
            nonlocal search_results
            search_results = []

            if config["cache"] and not update_cache:
                public_cached_results = search_public(media)
                if public_cached_results:
                    logger.info(
                        f"Found {len(public_cached_results)} public cached results"
                    )
                    public_cached_results = [
                        JackettResult().from_cached_item(torrent, media)
                        for torrent in public_cached_results
                        if len(torrent.get("hash", "")) == 40
                    ]
                    public_cached_results = filter_items(
                        public_cached_results, media, config=config
                    )
                    public_cached_results = torrent_service.convert_and_process(
                        public_cached_results
                    )
                    search_results.extend(public_cached_results)

            if config["zilean"] and len(search_results) < int(
                config["minCachedResults"]
            ):
                zilean_service = ZileanService(config)
                zilean_search_results = zilean_service.search(media)
                if zilean_search_results:
                    logger.info(
                        f"Found {len(zilean_search_results)} results from Zilean"
                    )
                    zilean_search_results = [
                        ZileanResult().from_api_cached_item(torrent, media)
                        for torrent in zilean_search_results
                        if len(torrent.get("infoHash", "")) == 40
                    ]
                    zilean_search_results = filter_items(
                        zilean_search_results, media, config=config
                    )
                    zilean_search_results = torrent_service.convert_and_process(
                        zilean_search_results
                    )
                    search_results = merge_items(search_results, zilean_search_results)

            if config["jackett"] and len(search_results) < int(
                config["minCachedResults"]
            ):
                jackett_service = JackettService(config)
                jackett_search_results = jackett_service.search(media)
                logger.info(f"Found {len(jackett_search_results)} results from Jackett")
                filtered_jackett_search_results = filter_items(
                    jackett_search_results, media, config=config
                )
                logger.info(
                    f"Filtered Jackett results: {len(filtered_jackett_search_results)}"
                )
                if filtered_jackett_search_results:
                    torrent_results = torrent_service.convert_and_process(
                        filtered_jackett_search_results
                    )
                    logger.debug(
                        f"Converted {len(torrent_results)} Jackett results to TorrentItems"
                    )
                    search_results = merge_items(search_results, torrent_results)

            if update_cache and search_results:
                logger.info(f"Updating cache with {len(search_results)} results")
                try:
                    cache_key = media_cache_key(media)
                    search_results_dict = [item.to_dict() for item in search_results]
                    redis_cache.set(cache_key, search_results_dict)
                except Exception as e:
                    logger.error(f"Error updating cache: {e}")

        perform_search()
        return search_results

    def get_and_filter_results(media, config):
        min_results = int(config.get("minCachedResults", 5))
        cache_key = media_cache_key(media)

        unfiltered_results = redis_cache.get(cache_key)
        if unfiltered_results is None:
            logger.info("No results in cache. Performing new search.")
            nocache_results = get_search_results(media, config)
            nocache_results_dict = [item.to_dict() for item in nocache_results]
            redis_cache.set(cache_key, nocache_results_dict)
            return nocache_results
        else:
            logger.info(f"Results retrieved from redis cache - {len(unfiltered_results)}.")
            unfiltered_results = [TorrentItem.from_dict(item) for item in unfiltered_results]

        filtered_results = filter_all_results(unfiltered_results, media)

        if len(filtered_results) < min_results:
            logger.info(
                f"Insufficient filtered results ({len(filtered_results)}). Performing new search."
            )
            redis_cache.delete(cache_key)
            unfiltered_results = get_search_results(media, config)
            unfiltered_results_dict = [item.to_dict() for item in unfiltered_results]
            redis_cache.set(cache_key, unfiltered_results_dict)
            filtered_results = filter_all_results(unfiltered_results, media)

        logger.info(f"Final number of filtered results: {len(filtered_results)}")
        return filtered_results

    search_results = get_and_filter_results(media, config)

    def stream_processing(search_results, media, config):
        torrent_smart_container = TorrentSmartContainer(search_results, media)

        if config["debrid"]:
            hashes = torrent_smart_container.get_hashes()
            ip = request.client.host
            result = debrid_service.get_availability_bulk(hashes, ip)
            torrent_smart_container.update_availability(
                result, type(debrid_service), media
            )
            logger.info(f"Checked availability for {len(result.items())} items")

        if config["cache"]:
            logger.debug("Caching public container items")
            torrent_smart_container.cache_container_items()

        best_matching_results = torrent_smart_container.get_best_matching()
        best_matching_results = sort_items(best_matching_results, config)
        logger.info(f"Found {len(best_matching_results)} best matching results")

        stream_list = parse_to_stremio_streams(best_matching_results, config, media)
        logger.info(f"Processed {len(stream_list)} streams for Stremio")

        return stream_list

    stream_list = stream_processing(search_results, media, config)
    streams = [Stream(**stream) for stream in stream_list]
    redis_cache.set(
        stream_cache_key(media), streams, expiration=3600
    )  # Make the cache expire after 1 hour TODO: Make this configurable
    total_time = time.time() - start
    logger.info(f"Request completed in {total_time:.2f} seconds")
    return SearchResponse(streams=streams)
