from RTN import parse

from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.logging_config import logger

class JackettResult:
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
        self.frenchlanguage = None # French Language Type
        self.typehdr = None # HDR / DV
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
            self.frenchlanguage,
            self.typehdr,
            self.indexer,
            self.privacy,
            self.type,
            self.parsed_data
        )

    def from_cached_item(self, cached_item, media):
        if type(cached_item) is not dict:
            logger.error(cached_item)

        self.info_hash = cached_item['hash']

        if len(self.info_hash) != 40:
            raise ValueError(f"The hash '{self.info_hash}' does not have the expected length of 40 characters.")
        
        parsed_result = parse(cached_item['title'])

        self.raw_title = cached_item['title']
        self.indexer = "Cache Public"  # Cache doesn't return an indexer sadly (It stores it tho)
        self.magnet = cached_item['magnet']
        self.link = cached_item['magnet']
        self.languages = cached_item['language'].split(";") if cached_item['language'] is not None else []
        self.seeders = cached_item['seeders']
        self.size = cached_item['size']
        self.type = media.type
        self.from_cache = True
        self.parsed_data = parsed_result

        return self
