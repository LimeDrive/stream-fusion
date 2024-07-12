from RTN import parse
from urllib.parse import quote

from stream_fusion.utils.models.media import Media
from stream_fusion.utils.models.series import Series
from stream_fusion.logging_config import logger


class TorrentItem:
    def __init__(self, raw_title, size, magnet, info_hash, link, seeders, languages, indexer,
                 privacy, type=None, parsed_data=None):
        self.logger = logger

        self.raw_title = raw_title  # Raw title of the torrent
        self.size = size  # Size of the video file inside the torrent - it may be updated during __process_torrent()
        self.magnet = magnet  # Magnet to torrent
        self.info_hash = info_hash  # Hash of the torrent
        self.link = link  # Link to download torrent file or magnet link
        self.seeders = seeders  # The number of seeders
        self.languages = languages  # Language of the torrent
        self.indexer = indexer  # Indexer of the torrent
        self.type = type  # "series" or "movie"
        self.privacy = privacy  # "public" or "private"

        self.file_name = None  # it may be updated during __process_torrent()
        self.files = None  # The files inside of the torrent. If it's None, it means that there is only one file inside of the torrent
        self.torrent_download = None  # The torrent jackett download url if its None, it means that there is only a magnet link provided by Jackett. It also means, that we cant do series file filtering before debrid.
        self.trackers = []  # Trackers of the torrent
        self.file_index = None  # Index of the file inside of the torrent - it may be updated durring __process_torrent() and update_availability(). If the index is None and torrent is not None, it means that the series episode is not inside of the torrent.

        self.availability = False  # If it's instantly available on the debrid service

        self.parsed_data = parsed_data  # Ranked result

    def to_debrid_stream_query(self, media: Media) -> dict:
        return {
            "magnet": self.magnet,
            "type": self.type,
            "file_index": self.file_index,
            "season": media.season if isinstance(media, Series) else None,
            "episode": media.episode if isinstance(media, Series) else None,
            "torrent_download": quote(self.torrent_download) if self.torrent_download is not None else None
        }
    
    def to_dict(self):
        return {
            'raw_title': self.raw_title,
            'size': self.size,
            'magnet': self.magnet,
            'info_hash': self.info_hash,
            'link': self.link,
            'seeders': self.seeders,
            'languages': self.languages,
            'indexer': self.indexer,
            'type': self.type,
            'privacy': self.privacy,
            'file_name': self.file_name,
            'files': self.files,
            'torrent_download': self.torrent_download,
            'trackers': self.trackers,
            'file_index': self.file_index,
            'availability': self.availability,
        }
    
    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            logger.error(f"Expected dict, got {type(data)}")
            return None

        instance = cls(
            raw_title=data['raw_title'],
            size=data['size'],
            magnet=data['magnet'],
            info_hash=data['info_hash'],
            link=data['link'],
            seeders=data['seeders'],
            languages=data['languages'],
            indexer=data['indexer'],
            privacy=data['privacy'],
            type=data['type']
        )
        
        instance.file_name = data['file_name']
        instance.files = data['files']
        instance.torrent_download = data['torrent_download']
        instance.trackers = data['trackers']
        instance.file_index = data['file_index']
        instance.availability = data['availability']
        
        instance.parsed_data = parse(instance.raw_title)

        return instance
