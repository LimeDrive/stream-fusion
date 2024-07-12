from RTN import parse

from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.logging_config import logger
from stream_fusion.utils.detection import detect_languages


class ZileanResult:
    def __init__(self):
        self.raw_title = None  # Raw title of the torrent
        self.size = None  # Size of the torrent
        self.link = None  # Download link for the torrent file or magnet url
        self.indexer = None  # Indexer
        self.seeders = None  # Seeders count
        self.magnet = None  # Magnet url
        self.info_hash = None  # infoHash by Jackett
        self.privacy = None  # public or private
        self.from_cache = None

        # Extra processed details for further filtering
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

    def from_api_cached_item(self, api_cached_item, media):
        if type(api_cached_item) is not dict:
            logger.error(api_cached_item)

        self.info_hash = api_cached_item['infoHash']
        if len(self.info_hash) != 40:
            raise ValueError(f"The hash '{self.info_hash}' does not have the expected length of 40 characters.")

        parsed_result = parse(api_cached_item['filename'])

        self.raw_title = parsed_result.raw_title
        self.indexer = "DMM API"
        self.magnet = "magnet:?xt=urn:btih:" + self.info_hash
        self.link = self.magnet
        self.languages = detect_languages(self.raw_title)
        self.seeders = 0
        self.size = api_cached_item['filesize']
        self.type = media.type
        self.privacy = "private"
        self.from_cache = True
        self.parsed_data = parsed_result

        return self
