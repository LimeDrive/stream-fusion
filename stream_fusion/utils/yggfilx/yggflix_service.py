from typing import List, Union
from RTN import parse

from stream_fusion.logging_config import logger
from stream_fusion.utils.detection import detect_languages
from stream_fusion.utils.yggfilx.yggflix_result import YggflixResult
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.settings import settings
from stream_fusion.utils.yggfilx.yggflix_api import YggflixAPI


class YggflixService:
    """Service for searching media on Yggflix."""

    def __init__(self, config: dict):
        self.yggflix = YggflixAPI()
        self.has_tmdb = config.get("metadataProvider") == "tmdb"
        self.ygg_url = settings.ygg_url
        self.ygg_passkey = config.get("yggPasskey")

    def search(self, media: Union[Movie, Series]) -> List[YggflixResult]:
        """
        Search for a media (movie or series) on Yggflix.

        Args:
            media (Union[Movie, Series]): The media to search for.

        Returns:
            List[YggflixResult]: List of search results.

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

    def __filter_out_no_seeders(self, results: List[dict]) -> List[dict]:
        """Filter out results with less than 5 seeders."""
        return [result for result in results if result.get("seeders", 0) >= 5]

    def __process_download_link(self, id: int) -> str:
        """Generate the download link for a given torrent."""
        if settings.ygg_lime_fix:
            return f"{settings.ygg_proxy_url}/api/torrent/{str(id)}?passkey={self.ygg_passkey}"
        return (
            f"{self.ygg_url}/engine/download_torrent?id={id}&passkey={self.ygg_passkey}"
        )

    def __search_movie(self, media: Movie) -> List[dict]:
        """Search for a movie on Yggflix."""
        if not self.has_tmdb:
            raise ValueError("Please use TMDB metadata provider for Yggflix")

        try:
            logger.info(f"Searching Yggflix for movie: {media.titles[0]}")
            # media_id = media.id[2:] if media.id.startswith("tt") else media.id
            return self.yggflix.get_movie_torrents(media.tmdb_id)
        except Exception as e:
            logger.error(
                f"Error searching Yggflix for movie: {media.titles[0]}", exc_info=True
            )
            return []

    def __search_series(self, media: Series) -> List[dict]:
        """Search for a series on Yggflix."""
        if not self.has_tmdb:
            raise ValueError("Please use TMDB metadata provider for Yggflix")

        try:
            logger.info(f"Searching Yggflix for series: {media.titles[0]}")
            # media_id = media.id[2:] if media.id.startswith("tt") else media.id
            return self.yggflix.get_tvshow_torrents(int(media.tmdb_id))
        except Exception as e:
            logger.error(
                f"Error searching Yggflix for series: {media.titles[0]}", exc_info=True
            )
            return []

    def __post_process_results(
        self, results: List[dict], media: Union[Movie, Series]
    ) -> List[YggflixResult]:
        """Process raw search results and convert them to YggflixResult objects."""
        if not results:
            logger.info(f"No results found on Yggflix for: {media.titles[0]}")
            return []

        results = self.__filter_out_no_seeders(results)
        logger.info(f"{len(results)} results found on Yggflix for: {media.titles[0]}")

        items = []
        for result in results:
            item = YggflixResult()

            item.raw_title=result["title"]
            item.size=result.get("size", 0)
            item.link=(
                self.__process_download_link(result.get("id"))
                if result.get("id")
                else None
            )
            item.indexer="API - Yggtorrent"
            item.seeders=result.get("seeders", 0)
            item.privacy="private"
            item.languages=detect_languages(item.raw_title)
            item.type=media.type
            item.parsed_data=parse(item.raw_title)

            items.append(item)

        return items
