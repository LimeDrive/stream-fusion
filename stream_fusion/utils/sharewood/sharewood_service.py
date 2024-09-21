import re
import urllib.parse
from typing import List, Union
from RTN import parse

from stream_fusion.logging_config import logger
from stream_fusion.utils.detection import detect_languages
from stream_fusion.utils.sharewood.sharewood_result import SharewoodResult
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.settings import settings
from stream_fusion.utils.sharewood.sharewood_api import SharewoodAPI


class SharewoodService:
    """Service for searching media on Sharewood."""

    def __init__(self, config: dict):
        self.sharewood_url = settings.sharewood_url
        if settings.sharewood_unique_account and settings.sharewood_passkey:
            self.sharewood_passkey = settings.sharewood_passkey
        else:
            self.sharewood_passkey = config.get("sharewoodPasskey")
        self.sharewood = SharewoodAPI(self.sharewood_passkey)

    def search(self, media: Union[Movie, Series]) -> List[SharewoodResult]:
        """
        Search for a media (movie or series) on sharewood.

        Args:
            media (Union[Movie, Series]): The media to search for.

        Returns:
            List[sharewoodResult]: List of search results.

        Raises:
            TypeError: If the media type is neither Movie nor Series.
        """
        if isinstance(media, Movie):
            results = self.__search_movie(media)
        elif isinstance(media, Series):
            results = self.__search_series(media)
        else:
            raise TypeError("Only Movie and Series types are allowed as media!")

        return self.__post_process_results(results, media)

    def __convert_size(self, size):
        units = {
            "b": 1,
            "kb": 1e3,
            "mb": 1e6,
            "gb": 1e9,
            "tb": 1e12,
            "pb": 1e15,
            "kib": 1024,
            "mib": 1024**2,
            "gib": 1024**3,
            "tib": 1024**4,
            "pib": 1024**5,
        }
        
        if isinstance(size, int):
            return size  # Si c'est déjà un entier, on le retourne tel quel
        
        if isinstance(size, str):
            size = size.lower().replace(',', '.')  # Remplace la virgule par un point pour les nombres décimaux
            parts = size.split()
            if len(parts) == 1:
                # Si une seule partie, on suppose que c'est en octets
                return int(float(parts[0]))
            elif len(parts) == 2:
                value, unit = parts
                value = float(value)
                if unit not in units:
                    raise ValueError(f"None support unit : {unit}")
                return int(value * units[unit])
        
        raise ValueError(f"unkound size format : {size}")

    def __clean_title(self, title):
        pronouns_to_remove = [
            "le",
            "la",
            "les",
            "l'",
            "un",
            "une",
            "des",
            "du",
            "de",
            "à",
            "au",
            "aux",
            "the",
            "a",
            "an",
            "some",
            "of",
            "to",
            "at",
            "in",
            "on",
            "for",
            "he",
            "she",
            "it",
            "they",
            "we",
            "you",
            "i",
            "me",
            "him",
            "her",
            "them",
            "us",
            "il",
            "elle",
            "on",
            "nous",
            "vous",
            "ils",
            "elles",
            "je",
            "tu",
            "moi",
            "toi",
            "lui",
        ]
        title = title.lower()
        title = re.sub(r"[^a-zA-Z0-9\s]", " ", title)
        words = title.split()
        words = [word for word in words if word not in pronouns_to_remove]
        cleaned_title = " ".join(words)
        cleaned_title = re.sub(r"\s+", " ", cleaned_title).strip()
        return cleaned_title

    def __deduplicate_api_results(self, api_results):
        unique_results = set()
        deduplicated_results = []

        for result in api_results:
            result_tuple = tuple(sorted(result.items()))

            if result_tuple not in unique_results:
                unique_results.add(result_tuple)
                deduplicated_results.append(result)

        return deduplicated_results

    def __remove_duplicate_titles(self, titles):
        seen = set()
        return [
            title
            for title in titles
            if not (title.lower() in seen or seen.add(title.lower()))
        ]

    def __search_movie(self, movie: Movie) -> List[dict]:
        unique_titles = self.__remove_duplicate_titles(movie.titles)
        clean_titles = [self.__clean_title(title) for title in unique_titles]
        results = []
        for title in clean_titles:
            results.extend(self.sharewood.search(query=title, category=1))
        return self.__deduplicate_api_results(results)

    def __search_series(self, series: Series) -> List[dict]:
        unique_titles = self.__remove_duplicate_titles(series.titles)
        clean_titles = [self.__clean_title(title) for title in unique_titles]
        search_texts = clean_titles.copy()

        if hasattr(series, "season") and hasattr(series, "episode"):
            search_texts.extend(
                [f"{title} {series.season}{series.episode}" for title in clean_titles]
            )

        results = []
        for text in search_texts:
            results.extend(self.sharewood.search(query=text, category=1))
        return self.__deduplicate_api_results(results)

    def __filter_out_no_seeders(self, results: List[dict]) -> List[dict]:
        """Filter out results with less than 5 seeders."""
        return [result for result in results if result.get("seeders", 0) >= 5]

    def __process_download_link(self, id: int) -> str:
        """Generate the download link for a given torrent."""
        return f"{self.sharewood_url}/api/{self.sharewood_passkey}/{id}/download"

    def __generate_magnet_link(self, info_hash: str, name: str) -> str:
        """Generate the magnet link for a given torrent."""
        encoded_name = urllib.parse.quote(name)
        tracker = f"{self.sharewood_url}/announce/{self.sharewood_passkey}"
        encoded_tracker = urllib.parse.quote(tracker)
        return f"magnet:?xt=urn:btih:{info_hash}&dn={encoded_name}&tr={encoded_tracker}"

    def __post_process_results(
        self, results: List[dict], media: Union[Movie, Series]
    ) -> List[SharewoodResult]:
        """Process raw search results and convert them to sharewoodResult objects."""
        if not results:
            logger.info(f"No results found on sharewood for: {media.titles[0]}")
            return []

        results = self.__filter_out_no_seeders(results)
        logger.info(f"{len(results)} results found on sharewood for: {media.titles[0]}")

        items = []
        for result in results:
            logger.debug(f"Processing result: {result}")
            item = SharewoodResult()

            item.raw_title = result.get("name", "...")
            item.info_hash = result.get("info_hash", None)
            item.size = self.__convert_size(result.get("size", 0))
            item.link = (
                self.__process_download_link(result.get("id"))
                if result.get("id")
                else None
            )
            item.magnet = self.__generate_magnet_link(item.info_hash, item.raw_title)
            item.indexer = "Sharewood - API"
            item.seeders = result.get("seeders", 0)
            item.privacy = "private"
            item.languages = detect_languages(item.raw_title, default_language="fr")
            item.type = media.type
            item.parsed_data = parse(item.raw_title)

            items.append(item)

        return items
