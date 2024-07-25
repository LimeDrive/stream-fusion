from RTN import parse

from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.logging_config import logger
from stream_fusion.utils.detection import detect_languages


class YggflixResult:
    def __init__(self):
        self.raw_title = None  # Raw title of the torrent
        self.size = None  # Size of the torrent
        self.link = None  # Contruct a magnet link here
        self.indexer = None  # Indexer
        self.seeders = None  # Seeders count
        self.magnet = None  # Magnet url
        self.info_hash = None  # infoHash by Jackett
        self.privacy = None  # public or private
        self.from_cache = None

        self.languages = None  # Language of the torrent
        self.type = None  # series or movie

        self.parsed_data = None  # Ranked result

    def convert_to_torrent_item(self):
        return TorrentItem(
            self.raw_title,
            self.size,
            self.magnet,
            self.info_hash.lower() if self.info_hash is not None else None,
            self.link,
            self.seeders,
            self.languages,
            self.indexer,
            self.privacy,
            self.type,
            self.parsed_data
        )
