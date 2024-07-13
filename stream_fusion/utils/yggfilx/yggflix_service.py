import re

from RTN import parse
from stream_fusion.logging_config import logger
from stream_fusion.services.ygg_conn.ygg_session import YggSessionManager
from stream_fusion.utils.detection import detect_languages
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.settings import settings
from stream_fusion.utils.yggfilx.yggflix_api import YggflixAPI


class YggflixService:
    def __init__(self, config):
        self.yggflix = YggflixAPI()
        self.has_tmdb = True if config.get("metadataProvider", "") == "tmdb" else False

    def search(self, media: Movie | Series):
        if isinstance(media, Movie):
            results = self.__search_movie(media)
        elif isinstance(media, Series):
            results = self.__search_series(media)
        else:
            raise TypeError("Only Movie and Series are allowed as media!")
        
        return self.__post_process_results(results, media)
    
    def __search_movie(self, media: Movie):
        try:
            if self.has_tmdb:
                logger.info(f"Searching yggflix for movie: {media.titles[0]}")
                api_results = self.yggflix.get_movie_torrents(media.id)
            else:
                raise Exception("Please use TMDB to use yggflix")
        except Exception as e:
            logger.error(f"Error searching yggflix for movie: {media.titles[0]}")

        results = []

    def __search_series(self, media: Series):
        try:
            if self.has_tmdb:
                logger.info(f"Searching yggflix for movie: {media.titles[0]}")
                api_results = self.yggflix.get_tvshow_torrents(media.id)
            else:
                raise Exception("Please use TMDB to use yggflix")
        except Exception as e:
            logger.error(f"Error searching yggflix for movie: {media.titles[0]}")

        results = []
        
    def __post_process_results(self, results, media):
        for result in results:
            parsed_result = parse(result.raw_title)
            
            result.parsed_data = parsed_result
            result.languages = detect_languages(result.raw_title)
            result.type = media.type

            if isinstance(media, Series):
                result.season = media.season
                result.episode = media.episode

        return results