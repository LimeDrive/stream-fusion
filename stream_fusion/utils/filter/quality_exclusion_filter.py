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
        if any(q.upper() in self.excluded_qualities for q in stream.parsed_data.quality):
            logger.debug(f"Stream excluded due to main quality: {stream.parsed_data.quality}")
            return False

        if stream.parsed_data.resolution:
            for item in stream.parsed_data.resolution:
                item_upper = item.upper()
                if item_upper in self.excluded_qualities:
                    logger.debug(f"Stream excluded due to quality spec: {item}")
                    return False
                if self.exclude_rips and item_upper in self.RIPS:
                    logger.debug(f"Stream excluded due to RIP: {item}")
                    return False
                if self.exclude_cams and item_upper in self.CAMS:
                    logger.debug(f"Stream excluded due to CAM: {item}")
                    return False

        logger.debug("Stream allowed")
        return True

    def can_filter(self) -> bool:
        return bool(self.excluded_qualities)
