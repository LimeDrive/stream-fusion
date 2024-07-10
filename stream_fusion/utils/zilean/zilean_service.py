import re
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

from stream_fusion.logging_config import logger
from stream_fusion.utils.models.movie import Movie
from stream_fusion.utils.models.series import Series
from stream_fusion.settings import settings


class ZileanService:
    def __init__(self, config):
        self.base_url = settings.zilean_url
        # TODO: check if possible to protect zilean endpoint.
        self.zilean_api_key = settings.zilean_api_key
        self.search_endpoint = "/dmm/search"
        self.session = requests.Session()
        self.logger = logger
        self.max_workers = settings.zilean_max_workers

    def search(self, media):
        if isinstance(media, Movie):
            return self.__search_movie(media)
        elif isinstance(media, Series):
            return self.__search_series(media)
        else:
            raise TypeError("Only Movie and Series are allowed as media!")
    
    # TODO: remove duplicate title from titles list
    def __clean_title(self, title):
        pronouns_to_remove = [
            'le', 'la', 'les', 'l\'', 'un', 'une', 'des', 'du', 'de', 'à', 'au', 'aux',
            'the', 'a', 'an', 'some', 'of', 'to', 'at', 'in', 'on', 'for',
            'he', 'she', 'it', 'they', 'we', 'you', 'i', 'me', 'him', 'her', 'them', 'us',
            'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'je', 'tu', 'moi', 'toi', 'lui'
        ]
        title = title.lower()
        title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
        words = title.split()
        words = [word for word in words if word not in pronouns_to_remove]
        cleaned_title = ' '.join(words)
        cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
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
        return [title for title in titles if not (title.lower() in seen or seen.add(title.lower()))]

    def __search_movie(self, movie):
        unique_titles = self.__remove_duplicate_titles(movie.titles)
        clean_titles = [self.__clean_title(title) for title in unique_titles]
        return self.__threaded_search(clean_titles)
    
    def __search_series(self, series):
        unique_titles = self.__remove_duplicate_titles(series.titles)
        clean_titles = [self.__clean_title(title) for title in unique_titles]
        search_texts = clean_titles.copy()

        if hasattr(series, 'season') and hasattr(series, 'episode'):
            search_texts.extend([f"{title} {series.season}{series.episode}" for title in clean_titles])

        return self.__threaded_search(search_texts)

    def __threaded_search(self, search_texts):
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_text = {executor.submit(self.__make_request, text): text for text in search_texts}
            for future in as_completed(future_to_text):
                results.extend(future.result())
        return self.__deduplicate_api_results(results)

    def __make_request(self, query_text):
        payload = {"queryText": query_text}
        headers = {"Content-Type": "application/json"}
        url = self.base_url + self.search_endpoint

        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            json_response = response.json()
            if isinstance(json_response, list):
                return json_response
            else:
                self.logger.warning(f"Unexpected response format for query: {query_text}")
                return []
        except Exception as e:
            self.logger.exception(f"An exception occurred while searching for '{query_text}' on Zilean: {str(e)}")
            return []