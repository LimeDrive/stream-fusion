import re

from stream_fusion.constants import FR_RELEASE_GROUPS
from stream_fusion.utils.filter.base_filter import BaseFilter
from stream_fusion.logging_config import logger


class LanguageFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)
        self.fr_regex_patterns = FR_RELEASE_GROUPS
        self.fr_regex = re.compile("|".join(self.fr_regex_patterns))

    def filter(self, data):
        filtered_data = []
        for torrent in data:
            if not torrent.languages:
                continue

            languages = torrent.languages.copy()

            if torrent.from_cache and "multi" in languages:
                regex = self.fr_regex.search(torrent.raw_title)
                logger.debug(f"Regex match for {torrent.raw_title} : {regex}")
                if not regex:
                    languages.remove("multi")
            
            if torrent.from_cache and "fr" in languages:
                regex = self.fr_regex.search(torrent.raw_title)
                logger.debug(f"Regex match for {torrent.raw_title} : {regex}")
                if not regex:
                    languages.remove("fr")

            if "multi" in languages or any(
                lang in self.config["languages"] for lang in languages
            ):
                torrent.languages = languages
                logger.debug(f"Keeping {torrent.raw_title} with lang : {languages} ")
                filtered_data.append(torrent)

        return filtered_data

    def can_filter(self):
        return self.config["languages"] is not None
