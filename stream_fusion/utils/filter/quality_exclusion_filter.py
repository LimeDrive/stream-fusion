from stream_fusion.utils.filter.base_filter import BaseFilter
from stream_fusion.logging_config import logger


class QualityExclusionFilter(BaseFilter):
    RIPS = {"HDRIP", "BRRIP", "BDRIP", "WEBRIP", "TVRIP", "VODRIP"}
    CAMS = {"CAM", "TS", "TC", "R5", "DVDSCR", "HDTV", "PDTV", "DSR", "WORKPRINT", "VHSRIP", "HDCAM"}

    def __init__(self, config: dict):
        super().__init__(config)
        self.excluded_qualities = {quality.upper() for quality in self.config.get('exclusion', [])}
        self.exclude_rips = "RIPS" in self.excluded_qualities
        self.exclude_cams = "CAM" in self.excluded_qualities

    def filter(self, data):
        return [
            stream for stream in data
            if self._is_stream_allowed(stream)
        ]

    def _is_stream_allowed(self, stream) -> bool:

        if stream.parsed_data.quality:
            quality_upper = stream.parsed_data.quality.upper()
            if quality_upper in self.excluded_qualities:
                logger.debug(f"Stream excluded due to main quality: {stream.parsed_data.quality}")
                return False

        if stream.parsed_data.resolution:
            resolution_upper = stream.parsed_data.resolution.upper()
            if resolution_upper in self.excluded_qualities:
                logger.debug(f"Stream excluded due to quality spec: {stream.parsed_data.resolution}")
                return False
            if self.exclude_rips and resolution_upper in self.RIPS:
                logger.debug(f"Stream excluded due to RIP: {stream.parsed_data.resolution}")
                return False
            if self.exclude_cams and resolution_upper in self.CAMS:
                logger.debug(f"Stream excluded due to CAM: {stream.parsed_data.resolution}")
                return False

        logger.debug("Stream allowed")
        return True

    def can_filter(self) -> bool:
        return bool(self.excluded_qualities)
