from stream_fusion.utils.filter.base_filter import BaseFilter
from stream_fusion.logging_config import logger


class MaxSizeFilter(BaseFilter):
    def __init__(self, config, additional_config=None):
        super().__init__(config, additional_config)
        self.max_size_bytes = int(self.config['maxSize']) * 1024 * 1024 * 1024  # Convertir Go en octets

    def filter(self, data):
        filtered_data = []
        for torrent in data:
            torrent_size = int(torrent.size) if isinstance(torrent.size, str) else torrent.size
            if torrent_size <= self.max_size_bytes:
                filtered_data.append(torrent)
            else:
                logger.debug(f"Excluded torrent due to size: {torrent.raw_title}, Size: {torrent_size / (1024*1024*1024):.2f} GB")
        logger.info(f"MaxSizeFilter: input {len(data)}, output {len(filtered_data)}")
        return filtered_data

    def can_filter(self):
        return int(self.config['maxSize']) > 0 and self.item_type == 'movie'

