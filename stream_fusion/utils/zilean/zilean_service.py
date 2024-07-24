import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Union

from stream_fusion.logging_config import logger
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.settings import settings
from zilean_api import ZileanAPI, DmmQueryRequest, ExtractedDmmEntry

class ZileanService:
    def __init__(self, config):
        self.zilean_api = ZileanAPI(settings.zilean_url)
        self.logger = logger
        self.max_workers = settings.zilean_max_workers

    def search(self, media: Union[Movie, Series]) -> List[ExtractedDmmEntry]:
        if isinstance(media, Movie):
            return self.__search_movie(media)
        elif isinstance(media, Series):
            return self.__search_series(media)
        else:
            raise TypeError("Only Movie and Series are allowed as media!")

    # def __clean_title(self, title: str) -> str:
    #     pronouns_to_remove = [
    #         'le', 'la', 'les', 'l\'', 'un', 'une', 'des', 'du', 'de', 'à', 'au', 'aux',
    #         'the', 'a', 'an', 'some', 'of', 'to', 'at', 'in', 'on', 'for',
    #         'he', 'she', 'it', 'they', 'we', 'you', 'i', 'me', 'him', 'her', 'them', 'us',
    #         'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'je', 'tu', 'moi', 'toi', 'lui'
    #     ]
    #     title = title.lower()
    #     title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
    #     words = title.split()
    #     words = [word for word in words if word not in pronouns_to_remove]
    #     cleaned_title = ' '.join(words)
    #     cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
    #     return cleaned_title

    def __deduplicate_api_results(self, api_results: List[ExtractedDmmEntry]) -> List[ExtractedDmmEntry]:
        unique_results = set()
        deduplicated_results = []

        for result in api_results:
            result_tuple = tuple(sorted(result.__dict__.items()))
            
            if result_tuple not in unique_results:
                unique_results.add(result_tuple)
                deduplicated_results.append(result)

        return deduplicated_results

    def __remove_duplicate_titles(self, titles: List[str]) -> List[str]:
        seen = set()
        return [title for title in titles if not (title.lower() in seen or seen.add(title.lower()))]

    def __search_movie(self, movie: Movie) -> List[ExtractedDmmEntry]:
        unique_titles = self.__remove_duplicate_titles(movie.titles)
        # clean_titles = [self.__clean_title(title) for title in unique_titles]
        return self.__threaded_search_movie(unique_titles)

    def __search_series(self, series: Series) -> List[ExtractedDmmEntry]:
        unique_titles = self.__remove_duplicate_titles(series.titles)
        # clean_titles = [self.__clean_title(title) for title in unique_titles]
        return self.__threaded_search_series(unique_titles, series)

    def __threaded_search_movie(self, search_texts: List[str]) -> List[ExtractedDmmEntry]:
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_text = {executor.submit(self.__make_movie_request, text): text for text in search_texts}
            for future in as_completed(future_to_text):
                results.extend(future.result())
        return self.__deduplicate_api_results(results)

    def __threaded_search_series(self, search_texts: List[str], series: Series) -> List[ExtractedDmmEntry]:
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_text = {executor.submit(self.__make_series_request, text, series): text for text in search_texts}
            for future in as_completed(future_to_text):
                results.extend(future.result())
        return self.__deduplicate_api_results(results)

    def __make_movie_request(self, query_text: str) -> List[ExtractedDmmEntry]:
        try:
            return self.zilean_api.dmm_search(DmmQueryRequest(queryText=query_text))
        except Exception as e:
            self.logger.exception(f"An exception occurred while searching for movie '{query_text}' on Zilean: {str(e)}")
            return []

    def __make_series_request(self, query_text: str, series: Series) -> List[ExtractedDmmEntry]:
        try:
            return self.zilean_api.dmm_filtered(
                query=query_text,
                season=getattr(series, 'season', None),
                episode=getattr(series, 'episode', None)
            )
        except Exception as e:
            self.logger.exception(f"An exception occurred while searching for series '{query_text}' on Zilean: {str(e)}")
            return []