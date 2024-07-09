from stream_fusion.utils.filter.base_filter import BaseFilter
from stream_fusion.logging_config import logger


class TitleExclusionFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)
        self.excluded_keywords = {keyword.upper() for keyword in self.config.get('exclusionKeywords', [])}

    def filter(self, data):
        filtered_items = []
        for stream in data:
            if self._should_include_stream(stream):
                filtered_items.append(stream)
        
        logger.info(f"TitleExclusionFilter: input {len(data)}, output {len(filtered_items)}")
        return filtered_items

    def _should_include_stream(self, stream):
        try:
            title_upper = stream.raw_title.upper()
            for keyword in self.excluded_keywords:
                if keyword in title_upper:
                    logger.debug(f"Excluded stream: {stream.raw_title} (keyword: {keyword})")
                    return False
            return True
        except AttributeError:
            logger.warning(f"Stream has no title attribute: {stream}")
            return False

    def can_filter(self):
        return bool(self.excluded_keywords)
