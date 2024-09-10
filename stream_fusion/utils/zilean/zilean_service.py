import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Union

from stream_fusion.logging_config import logger
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.settings import settings
from stream_fusion.utils.zilean.zilean_api import ZileanAPI, DMMQueryRequest, DMMTorrentInfo

class ZileanService:
    def __init__(self, config):
        self.zilean_api = ZileanAPI()
        self.logger = logger
        self.max_workers = settings.zilean_max_workers

    def search(self, media: Union[Movie, Series]) -> List[DMMTorrentInfo]:
        if isinstance(media, Movie):
            return self.__search_movie(media)
        elif isinstance(media, Series):
            return self.__search_series(media)
        else:
            raise TypeError("Only Movie and Series are allowed as media!")

    def __deduplicate_api_results(self, api_results: List[DMMTorrentInfo]) -> List[DMMTorrentInfo]:
        unique_results = set()
        deduplicated_results = []
        for result in api_results:
            result_tuple = (
                result.raw_title,
                result.info_hash,
                result.size,
            )
            if result_tuple not in unique_results:
                unique_results.add(result_tuple)
                deduplicated_results.append(result)
        return deduplicated_results

    def __remove_duplicate_titles(self, titles: List[str]) -> List[str]:
        seen = set()
        return [title for title in titles if not (title.lower() in seen or seen.add(title.lower()))]

    def __search_movie(self, movie: Movie) -> List[DMMTorrentInfo]:
        unique_titles = self.__remove_duplicate_titles(movie.titles)
        keyword_results = self.__threaded_search_movie(unique_titles)
        
        # Search by IMDb ID
        imdb_results = self.__search_by_imdb_id(movie.id)
        
        # Combine and deduplicate results
        all_results = keyword_results + imdb_results
        return self.__deduplicate_api_results(all_results)

    def __search_series(self, series: Series) -> List[DMMTorrentInfo]:
        unique_titles = self.__remove_duplicate_titles(series.titles)
        keyword_results = self.__threaded_search_series(unique_titles, series)
        
        # Search by IMDb ID
        imdb_results = self.__search_by_imdb_id(series.id)
        
        # Combine and deduplicate results
        all_results = keyword_results + imdb_results
        return self.__deduplicate_api_results(all_results)

    def __threaded_search_movie(self, search_texts: List[str]) -> List[DMMTorrentInfo]:
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_text = {executor.submit(self.__make_movie_request, text): text for text in search_texts}
            for future in as_completed(future_to_text):
                results.extend(future.result())
        return results

    def __threaded_search_series(self, search_texts: List[str], series: Series) -> List[DMMTorrentInfo]:
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_text = {executor.submit(self.__make_series_request, text, series): text for text in search_texts}
            for future in as_completed(future_to_text):
                results.extend(future.result())
        return results

    def __make_movie_request(self, query_text: str) -> List[DMMTorrentInfo]:
        try:
            return self.zilean_api.dmm_search(DMMQueryRequest(queryText=query_text))
        except Exception as e:
            self.logger.exception(f"An exception occurred while searching for movie '{query_text}' on Zilean: {str(e)}")
            return []

    def __make_series_request(self, query_text: str, series: Series) -> List[DMMTorrentInfo]:
        try:
            season = getattr(series, 'season', None)
            episode = getattr(series, 'episode', None)
            
            if season is not None:
                season = season.lstrip('S') if isinstance(season, str) else season
            if episode is not None:
                episode = episode.lstrip('E') if isinstance(episode, str) else episode
            
            return self.zilean_api.dmm_filtered(
                query=query_text,
                season=season,
                episode=episode
            )
        except Exception as e:
            self.logger.exception(f"An exception occurred while searching for series '{query_text}' on Zilean: {str(e)}")
            return []

    def __search_by_imdb_id(self, imdb_id: str) -> List[DMMTorrentInfo]:
        try:
            return self.zilean_api.dmm_filtered(imdb_id=imdb_id)
        except Exception as e:
            self.logger.exception(f"An exception occurred while searching for IMDb ID '{imdb_id}' on Zilean: {str(e)}")
            return []