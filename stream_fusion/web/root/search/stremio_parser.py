import json
import queue
import threading
from typing import List
from RTN import ParsedData

from stream_fusion.utils.models.media import Media
from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.utils.string_encoding import encodeb64
from stream_fusion.utils.detection import detect_audios_type
from stream_fusion.logging_config import logger


INSTANTLY_AVAILABLE = "[⚡]"
DOWNLOAD_REQUIRED = "[⬇️]"
DIRECT_TORRENT = "[🏴‍☠️]"


# TODO: Languages
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


def parse_to_debrid_stream(torrent_item: TorrentItem, configb64, host, torrenting, results: queue.Queue, media: Media):
    if torrent_item.availability == True:
        name = f"{INSTANTLY_AVAILABLE}\n"
    else:
        name = f"{DOWNLOAD_REQUIRED}\n"

    parsed_data = torrent_item.parsed_data.data
    logger.debug(f"Parsed data: {parsed_data}")

    resolution = parsed_data.resolution[0] if parsed_data.resolution else "Unknow"
    name += f"{resolution}"

    if parsed_data.quality:
        name += f"\n({'|'.join(parsed_data.quality)})"

    size_in_gb = round(int(torrent_item.size) / 1024 / 1024 / 1024, 2)

    title = f"{parsed_data.raw_title}\n"

    if media.type == "series" and torrent_item.file_name is not None:
       title += f"{torrent_item.file_name}\n"

    title += f"👥  {torrent_item.seeders}   💾  {size_in_gb}GB   🔍  {torrent_item.indexer}\n"
    
    if parsed_data.codec:
        title += f"🎥  {', '.join(parsed_data.codec)}   {'.'.join(parsed_data.hdr)}\n"
    else:
        title += f"🎥  {'.'.join(parsed_data.hdr)}\n"

    audio_type = detect_audios_type(parsed_data.raw_title, torrent_item.languages)
    audio_info = []

    if audio_type:
        audio_info.append(audio_type)

    if parsed_data.audio:
        audio_info.extend(parsed_data.audio)

    if audio_info:
        title += f"🎧  {' | '.join(audio_info)}\n"
    
    if torrent_item.languages:
        title += "/".join(get_emoji(language) for language in torrent_item.languages)
    else:
        title += "🌐"

    queryb64 = encodeb64(json.dumps(torrent_item.to_debrid_stream_query(media))).replace('=', '%3D')

    results.put({
        "name": name,
        "description": title,
        "url": f"{host}/playback/{configb64}/{queryb64}",
        "behaviorHints":{
            "bingeGroup": f"stremio-jackett-{torrent_item.info_hash}",
            "filename": torrent_item.file_name if torrent_item.file_name is not None else torrent_item.raw_title # TODO: Use parsed title?
        }
    })

    if torrenting and torrent_item.privacy == "public":
        name = f"{DIRECT_TORRENT}\n{parsed_data.quality}\n"
        if len(parsed_data.quality) > 0 and parsed_data.quality[0] != "Unknown" and \
                parsed_data.quality[0] != "":
            name += f"({'|'.join(parsed_data.quality)})"
        results.put({
            "name": name,
            "description": title,
            "infoHash": torrent_item.info_hash,
            "fileIdx": int(torrent_item.file_index) if torrent_item.file_index else None,
            "behaviorHints":{
                "bingeGroup": f"stremio-jackett-{torrent_item.info_hash}",
                "filename": torrent_item.file_name if torrent_item.file_name is not None else torrent_item.raw_title # TODO: Use parsed title?
            }
            # "sources": ["tracker:" + tracker for tracker in torrent_item.trackers]
        })


def parse_to_stremio_streams(torrent_items: List[TorrentItem], config, media):
    stream_list = []
    threads = []
    thread_results_queue = queue.Queue()

    configb64 = encodeb64(json.dumps(config).replace('=', '%3D'))
    for torrent_item in torrent_items[:int(config['maxResults'])]:
        thread = threading.Thread(target=parse_to_debrid_stream,
                                  args=(torrent_item, configb64, config['addonHost'], config['torrenting'],
                                        thread_results_queue, media),
                                  daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    while not thread_results_queue.empty():
        stream_list.append(thread_results_queue.get())

    if len(stream_list) == 0:
        return []

    if config['debrid']:
        stream_list = sorted(stream_list, key=filter_by_availability)
        stream_list = sorted(stream_list, key=filter_by_direct_torrnet)
    return stream_list
