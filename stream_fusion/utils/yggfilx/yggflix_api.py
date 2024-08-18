from typing import List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

        This constructor sets up the API client with connection pooling and retry strategies.

        Args:
            pool_connections (int): Number of connection pools to cache. Defaults to 10.
            pool_maxsize (int): Maximum number of connections to save in the pool. Defaults to 10.
            max_retries (int): Maximum number of retries for failed requests. Defaults to 3.
            timeout (int): Timeout for requests in seconds. Defaults to 10.

        Note:
            The base URL for the API is set using the settings.yggflix_url value.
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

        This method handles the actual HTTP request, including error handling and logging.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint (the part of the URL after the base URL)
            params (dict, optional): Query parameters to include in the request. Defaults to None.

        Returns:
            dict: JSON response from the API

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs
            requests.exceptions.ConnectionError: If a connection error occurs
            requests.exceptions.Timeout: If the request times out
            requests.exceptions.RequestException: For any other request-related errors
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
        """
        Perform a search on the API.

        Args:
            query (str, optional): The search query. Defaults to an empty string.

        Returns:
            dict: JSON response containing search results
        """
        return self._make_request("GET", "/search", params={"q": query})

    def get_home(self):
        """
        Get home page data from the API.

        Returns:
            dict: JSON response containing home page data
        """
        return self._make_request("GET", "/home")

    def get_movie_detail(self, movie_id: int):
        """
        Get details of a specific movie.

        Args:
            movie_id (int): The unique identifier of the movie

        Returns:
            dict: JSON response containing movie details
        """
        return self._make_request("GET", f"/movie/{movie_id}")

    def get_movie_torrents(self, movie_id: int):
        """
        Get torrents associated with a specific movie.

        Args:
            movie_id (int): The unique identifier of the movie

        Returns:
            dict: JSON response containing torrent information for the movie
        """
        return self._make_request("GET", f"/movie/{movie_id}/torrents")

    def get_tvshow_detail(self, tvshow_id: int):
        """
        Get details of a specific TV show.

        Args:
            tvshow_id (int): The unique identifier of the TV show

        Returns:
            dict: JSON response containing TV show details
        """
        return self._make_request("GET", f"/tvshow/{tvshow_id}")

    def get_tvshow_torrents(self, tvshow_id: int):
        """
        Get torrents associated with a specific TV show.

        Args:
            tvshow_id (int): The unique identifier of the TV show

        Returns:
            dict: JSON response containing torrent information for the TV show
        """
        return self._make_request("GET", f"/tvshow/{tvshow_id}/torrents")

    def get_torrents(
        self,
        page: int = 1,
        q: str = "",
        category_id: Optional[int] = None,
        order_by: str = "uploaded_at",
    ) -> List[dict]:
        """
        Get a list of torrents with optional filtering and sorting.

        Args:
            page (int): Page number for pagination. Defaults to 1.
            q (str): Search query. Defaults to an empty string.
            category_id (int, optional): Category ID for filtering. Defaults to None.
            order_by (str): Field to order results by. Can be "uploaded_at", "seeders", or "downloads".
                            Defaults to "uploaded_at".

        Returns:
            List[dict]: A list of torrent results.
        """
        params = {"page": page, "q": q, "order_by": order_by}
        if category_id is not None:
            params["category_id"] = category_id

        return self._make_request("GET", "/torrents", params=params)

    def get_torrent_detail(self, torrent_id: int) -> dict:
        """
        Get detailed information about a specific torrent.

        Args:
            torrent_id (int): The unique identifier of the torrent.

        Returns:
            dict: Detailed information about the torrent.
        """
        return self._make_request("GET", f"/torrent/{torrent_id}")

    def download_torrent(self, torrent_id: int, passkey: str) -> bytes:
        """
        Download a specific torrent file.

        Args:
            torrent_id (int): The unique identifier of the torrent to download.
            passkey (str): A 32-character passkey for authentication.

        Returns:
            bytes: The raw content of the .torrent file.

        Raises:
            ValueError: If the passkey is not exactly 32 characters long.
            requests.exceptions.HTTPError: If an HTTP error occurs during the download.
            requests.exceptions.RequestException: For any other request-related errors.
        """
        if len(passkey) != 32:
            raise ValueError("Passkey must be exactly 32 characters long.")

        url = f"{self.base_url}/torrent/{torrent_id}/download"
        params = {"passkey": passkey}

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred while downloading torrent: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while downloading torrent: {e}")
            raise

    def __del__(self):
        """
        Close the session when the object is destroyed.

        This destructor ensures that the requests session is properly closed,
        freeing up system resources.
        """
        self.session.close()
