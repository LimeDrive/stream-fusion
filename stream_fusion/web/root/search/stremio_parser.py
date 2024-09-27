import json
import queue
import re
import threading
from typing import List

from RTN import ParsedData

from stream_fusion.constants import FR_RELEASE_GROUPS, FRENCH_PATTERNS
from stream_fusion.utils.models.media import Media
from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.utils.string_encoding import encodeb64


INSTANTLY_AVAILABLE = "⚡"
DOWNLOAD_REQUIRED = "⬇️"
DIRECT_TORRENT = "🏴‍☠️"


def get_emoji(language):
    emoji_dict = {
        "fr": "🇫🇷 FRENCH",
        "en": "🇬🇧 ENGLISH",
        "es": "🇪🇸 SPANISH",
        "de": "🇩🇪 GERMAN",
        "it": "🇮🇹 ITALIAN",
        "pt": "🇵🇹 PORTUGUESE",
        "ru": "🇷🇺 RUSSIAN",
        "in": "🇮🇳 INDIAN",
        "nl": "🇳🇱 DUTCH",
        "hu": "🇭🇺 HUNGARIAN",
        "la": "🇲🇽 LATINO",
        "multi": "🌍 MULTi",
    }
    return emoji_dict.get(language, "🇬🇧")


def filter_by_availability(item):
    if item["name"].startswith(INSTANTLY_AVAILABLE):
        return 0
    else:
        return 1


def filter_by_direct_torrnet(item):
    if item["name"].startswith(DIRECT_TORRENT):
        return 1
    else:
        return 0


def extract_release_group(title):
    combined_pattern = "|".join(FR_RELEASE_GROUPS)
    match = re.search(combined_pattern, title)
    return match.group(0) if match else None


def detect_french_language(title):
    for language, pattern in FRENCH_PATTERNS.items():
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return language
    return None


def parse_to_debrid_stream(
    torrent_item: TorrentItem,
    configb64,
    host,
    torrenting,
    results: queue.Queue,
    media: Media,
):
    if torrent_item.availability:
        name = f"{INSTANTLY_AVAILABLE}|–{torrent_item.availability}-|{INSTANTLY_AVAILABLE}"
    else:
        name = f"{DOWNLOAD_REQUIRED}|–DL-|{DOWNLOAD_REQUIRED}"

    parsed_data: ParsedData = torrent_item.parsed_data

    resolution = parsed_data.resolution if parsed_data.resolution else "Unknow"
    name += f"\n |_{resolution}_|"

    size_in_gb = round(int(torrent_item.size) / 1024 / 1024 / 1024, 2)

    title = f"{torrent_item.raw_title}\n"

    if media.type == "series" and torrent_item.file_name is not None:
        title += f"{torrent_item.file_name}\n"

    if torrent_item.languages:
        title += "/".join(get_emoji(language) for language in torrent_item.languages)
    else:
        title += "🌐"
    groupe = extract_release_group(torrent_item.raw_title)
    lang_type = detect_french_language(torrent_item.raw_title)
    if lang_type:
        title += f"  ✔ {lang_type} "
    if groupe:
        title += f"  ☠️ {groupe}"
    elif parsed_data.group:
        title += f"  ☠️ {parsed_data.group}"
    title += "\n"

    title += (
        f"👥 {torrent_item.seeders}   💾 {size_in_gb}GB   🔍 {torrent_item.indexer}\n"
    )

    if parsed_data.codec:
        title += f"🎥 {parsed_data.codec} "
    if parsed_data.quality:
        title += f"📺 {parsed_data.quality} "
    if parsed_data.audio:
        title += f"🎧 {' '.join(parsed_data.audio)}"
    if parsed_data.codec or parsed_data.audio or parsed_data.resolution:
        title += "\n"


    queryb64 = encodeb64(
        json.dumps(torrent_item.to_debrid_stream_query(media))
    ).replace("=", "%3D")

    results.put(
        {
            "name": name,
            "description": title,
            "url": f"{host}/playback/{configb64}/{queryb64}",
            "behaviorHints": {
                "bingeGroup": f"stremio-jackett-{torrent_item.info_hash}",
                "filename": (
                    torrent_item.file_name
                    if torrent_item.file_name is not None
                    else torrent_item.raw_title
                ),
            },
        }
    )

    if torrenting and torrent_item.privacy == "public":
        name = f"{DIRECT_TORRENT}\n{parsed_data.quality}\n"
        if (
            len(parsed_data.quality) > 0
            and parsed_data.quality[0] != "Unknown"
            and parsed_data.quality[0] != ""
        ):
            name += f"({'|'.join(parsed_data.quality)})"
        results.put(
            {
                "name": name,
                "description": title,
                "infoHash": torrent_item.info_hash,
                "fileIdx": (
                    int(torrent_item.file_index) if torrent_item.file_index else None
                ),
                "behaviorHints": {
                    "bingeGroup": f"stremio-jackett-{torrent_item.info_hash}",
                    "filename": (
                        torrent_item.file_name
                        if torrent_item.file_name is not None
                        else torrent_item.raw_title
                    ),
                },
                # "sources": ["tracker:" + tracker for tracker in torrent_item.trackers]
            }
        )


def parse_to_stremio_streams(torrent_items: List[TorrentItem], config, media):
    stream_list = []
    threads = []
    thread_results_queue = queue.Queue()

    configb64 = encodeb64(json.dumps(config).replace("=", "%3D"))
    for torrent_item in torrent_items[: int(config["maxResults"])]:
        thread = threading.Thread(
            target=parse_to_debrid_stream,
            args=(
                torrent_item,
                configb64,
                config["addonHost"],
                config["torrenting"],
                thread_results_queue,
                media,
            ),
            daemon=True,
        )
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    while not thread_results_queue.empty():
        stream_list.append(thread_results_queue.get())

    if len(stream_list) == 0:
        return []

    if config["debrid"]:
        stream_list = sorted(stream_list, key=filter_by_availability)
        stream_list = sorted(stream_list, key=filter_by_direct_torrnet)
    return stream_list
