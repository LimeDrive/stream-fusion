import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

from stream_fusion.settings import settings
from stream_fusion.logging_config import logger


class YggflixAPI:
    def __init__(
        self,
        pool_connections=10,
        pool_maxsize=10,
        max_retries=3,
        timeout=10,
    ):
        """
        Initialize the YggflixAPI class.

        :param base_url: Base URL for the API
        :param pool_connections: Number of connection pools to cache
        :param pool_maxsize: Maximum number of connections to save in the pool
        :param max_retries: Maximum number of retries for failed requests
        :param timeout: Timeout for requests in seconds
        """
        self.base_url = f"{settings.yggflix_url}/api"
        self.timeout = timeout
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _make_request(self, method, endpoint, params=None):
        """
        Make an HTTP request to the API.

        :param method: HTTP method (GET, POST, etc.)
        :param endpoint: API endpoint
        :param params: Query parameters
        :return: JSON response
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method, url, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error occurred: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error occurred: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred during the request: {e}")
            raise

    def search(self, query=""):
        """Perform a search."""
        return self._make_request("GET", "/search", params={"q": query})

    def get_movie_detail(self, movie_id: int):
        """Get details of a movie."""
        return self._make_request("GET", f"/movie/{movie_id}")

    def get_movie_torrents(self, movie_id: int):
        """Get torrents for a movie."""
        return self._make_request("GET", f"/movie/{movie_id}/torrents")

    def get_tvshow_detail(self, tvshow_id: int):
        """Get details of a TV show."""
        return self._make_request("GET", f"/tvshow/{tvshow_id}")
    
    def get_tvshow_torrents(self, tvshow_id: int):
        """Get torrents for a TV show."""
        return self._make_request("GET", f"/tvshow/{tvshow_id}/torrents")
    
    def get_torrent_info(self, torrent_id: int):
        """Get details of a torrent."""
        return self._make_request("GET", f"/torrent/{torrent_id}")
    
    def get_torrent(self, page: int = 1):
        """Get details of a torrent."""
        return self._make_request("GET", f"/torrents?page={page}")
    
    def __del__(self):
        """Close the session when the object is destroyed."""
        self.session.close()
