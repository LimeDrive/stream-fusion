from stream_fusion.utils.filter.base_filter import BaseFilter
from stream_fusion.logging_config import logger
from stream_fusion.utils.torrent.torrent_item import TorrentItem


class QualityExclusionFilter(BaseFilter):
    RIPS = {"HDRIP", "BRRIP", "BDRIP", "WEBRIP", "TVRIP", "VODRIP"}
    CAMS = {"CAM", "TS", "TC", "R5", "DVDSCR", "HDTV", "PDTV", "DSR", "WORKPRINT", "VHSRIP", "HDCAM"}

    def __init__(self, config: dict):
        super().__init__(config)
        self.excluded_qualities = {quality.upper() for quality in self.config.get('exclusion', [])}
        self.exclude_rips = "RIPS" in self.excluded_qualities
        self.exclude_cams = "CAM" in self.excluded_qualities
        self.exclude_hevc = "HEVC" in self.excluded_qualities

    def filter(self, data):
        return [
            stream for stream in data
            if self._is_stream_allowed(stream)
        ]

    def _is_stream_allowed(self, stream: TorrentItem) -> bool:

        parsed_data = stream.parsed_data

        if parsed_data.quality:
            quality_upper = parsed_data.quality.upper()
            if quality_upper in self.excluded_qualities:
                logger.debug(f"Stream excluded due to {parsed_data.quality} quality : {parsed_data.raw_title}")
                return False

        if parsed_data.resolution:
            resolution_upper = parsed_data.resolution.upper()
            if resolution_upper in self.excluded_qualities:
                logger.debug(f"Stream excluded due to quality spec ( {parsed_data.resolution} ): {parsed_data.raw_title}")
                return False
            if self.exclude_rips and resolution_upper in self.RIPS:
                logger.debug(f"Stream excluded due to RIP: {parsed_data.raw_title}")
                return False
            if self.exclude_cams and resolution_upper in self.CAMS:
                logger.debug(f"Stream excluded due to CAM: {parsed_data.raw_title}")
                return False
        
        if parsed_data.codec:
            codec_upper = parsed_data.codec.upper()
            if self.exclude_hevc and codec_upper == "HEVC":
                logger.debug(f"Stream excluded due to HEVC codec: {parsed_data.raw_title}")
                return False

        return True

    def can_filter(self) -> bool:
        return bool(self.excluded_qualities)
