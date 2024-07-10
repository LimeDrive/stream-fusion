import os
import json
# import copy
# import redis
# import pickle
# import hashlib
import requests

from typing import List

from stream_fusion.logging_config import logger
from stream_fusion.utils.torrent.torrent_item import TorrentItem
# from stream_fusion.utils.jackett.jackett_result import JackettResult
from stream_fusion.constants import CACHER_URL, EXCLUDED_TRACKERS
# from stream_fusion.utils.models.movie import Movie
# from stream_fusion.utils.models.series import Series

# Redis connection initialization
# redis_client = redis.Redis(host="redis", port=6379)

# CACHE_EXPIRATION_TIME = 48 * 60 * 60

# def cache_key(media):
#     if isinstance(media, Movie):
#         key_string = f"movie:{media.titles[0]}:{media.languages[0]}"
#     elif isinstance(media, Series):
#         key_string = f"series:{media.titles[0]}:{media.languages[0]}:{media.season}"
#     else:
#         raise TypeError("Only Movie and Series are allowed as media!")
#     hashed_key = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
#     return hashed_key[:16]

# def search_redis(media):
#     try:
#         logger.info(f"Searching for cached {media.type} results")
#         hash_key = cache_key(media)
#         cached_result = redis_client.hgetall(hash_key)
        
#         if cached_result:
#             return [pickle.loads(value) for value in cached_result.values()]
#         else:
#             return []
#     except Exception as e:
#         logger.error(f"Error in search_cache: {str(e)}")
#         return []

# def cache_redis(torrents: List[JackettResult], media):
#     if os.getenv("NODE_ENV") == "development":
#         return

#     logger.info("Started caching results")

#     cached_torrents = {}
#     for index, torrent in enumerate(torrents):
#         try:
#             cached_torrent = copy.deepcopy(torrent)
#             cached_torrent.indexer = "Locally cached"
#             cached_torrents[str(index)] = pickle.dumps(cached_torrent)
#         except Exception as e:
#             logger.error(f"Failed to create cached copy of torrent: {str(e)}")

#     try:
#         hash_key = cache_key(media)
#         redis_client.hmset(hash_key, cached_torrents)
#         redis_client.expire(hash_key, CACHE_EXPIRATION_TIME)

#         logger.info(f"Cached {len(cached_torrents)} {media.type} results")
#     except Exception as e:
#         logger.error(f"Failed to cache results: {str(e)}")


def search_public(media):
    logger.info("Searching for public cached " + media.type + " results")
    url = CACHER_URL + "getResult/" + media.type + "/"
    # Without that, the cache doesn't return results. Maybe make multiple requests? One for each language, just like jackett?
    cache_search = media.__dict__
    cache_search["title"] = cache_search["titles"][0]
    cache_search["language"] = cache_search["languages"][0]
    # TODO: Wtf, why do we need to use __dict__ here? And also, why is it stuck when we use media directly?
    response = requests.get(url, json=cache_search)
    return response.json()


def cache_public(torrents: List[TorrentItem], media):
    if os.getenv("NODE_ENV") == "development":
        return

    logger.info("Started Public Caching results")

    cache_items = []
    for torrent in torrents:
        if torrent.indexer in EXCLUDED_TRACKERS:
            continue

        try:
            cache_item = dict()

            cache_item["title"] = torrent.raw_title
            cache_item["trackers"] = "tracker:".join(torrent.trackers)
            cache_item["magnet"] = torrent.magnet
            cache_item["files"] = []  # I guess keep it empty?
            cache_item["hash"] = torrent.info_hash
            cache_item["indexer"] = torrent.indexer
            cache_item["quality"] = (
                torrent.parsed_data.resolution[0]
                if len(torrent.parsed_data.resolution) > 0
                else "Unknown"
            )
            cache_item["qualitySpec"] = ";".join(torrent.parsed_data.quality)
            cache_item["seeders"] = torrent.seeders
            cache_item["size"] = torrent.size
            cache_item["language"] = ";".join(torrent.languages)
            cache_item["type"] = media.type
            cache_item["availability"] = torrent.availability

            if media.type == "movie":
                cache_item["year"] = media.year
            elif media.type == "series":
                cache_item["season"] = media.season
                cache_item["episode"] = media.episode
                cache_item["seasonfile"] = (
                    False  # I guess keep it false to not mess up results?
                )

            cache_items.append(cache_item)
        except:
            logger.exception("An exception occured durring public cache parsing")
            pass

    try:
        url = f"{CACHER_URL}pushResult/{media.type}"
        cache_data = json.dumps(cache_items, indent=4)
        response = requests.post(url, data=cache_data)
        response.raise_for_status()

        if response.status_code == 200:
            logger.info(f"Cached {str(len(cache_items))} {media.type} results on Public Cache")
        else:
            logger.error(f"Failed to public cache {media.type} results: {str(response)}")
    except:
        logger.error("Failed to public cache results")
        pass
