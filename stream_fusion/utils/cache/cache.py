import os
import json
import requests

from typing import List

from stream_fusion.logging_config import logger
from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.constants import EXCLUDED_TRACKERS
from stream_fusion.settings import settings

def search_public(media):
    logger.info("Searching for public cached " + media.type + " results")
    url = settings.public_cache_url + "getResult/" + media.type + "/"
    # Without that, the cache doesn't return results. Maybe make multiple requests? One for each language, just like jackett?
    cache_search = media.__dict__
    cache_search["title"] = cache_search["titles"][0]
    cache_search["language"] = cache_search["languages"][0]
    #  Wtf, why do we need to use __dict__ here? And also, why is it stuck when we use media directly?
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
                torrent.parsed_data.resolution
                if torrent.parsed_data.resolution
                else "Unknown"
            )
            cache_item["qualitySpec"] = ";".join(torrent.parsed_data.quality)
            cache_item["seeders"] = torrent.seeders
            cache_item["size"] = torrent.size
            cache_item["language"] = ";".join(torrent.languages)
            cache_item["type"] = media.type
            cache_item["availability"] = False

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
        url = f"{settings.public_cache_url}pushResult/{media.type}"
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
