import time
from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter

from stream_fusion.settings import settings
from stream_fusion.logging_config import logger


class RateLimiter:
    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.last_call = 0

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time.time()
            time_since_last_call = now - self.last_call
            if time_since_last_call < 1 / self.calls_per_second:
                time.sleep(1 / self.calls_per_second - time_since_last_call)
            self.last_call = time.time()
            return func(*args, **kwargs)

        return wrapper


class SharewoodAPI:
    def __init__(
        self,
        sharewood_passkey: str,
        pool_connections=10,
        pool_maxsize=10,
        max_retries=3,
        timeout=10,
    ):
        self.base_url = f"{settings.sharewood_url}/api"
        if not sharewood_passkey or len(sharewood_passkey) != 32:
            raise ValueError("Sharewood passkey must be 32 characters long")
        self.sharewood_passkey = sharewood_passkey
        self.timeout = timeout
        self.session = requests.Session()
        self.rate_limiter = RateLimiter(calls_per_second=1)

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

    @RateLimiter()
    def _make_request(self, method, endpoint, params=None):
        url = f"{self.base_url}/{self.sharewood_passkey}/{endpoint}"
        try:
            response = self.session.request(
                method, url, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred during the request: {e}")
            raise

    def get_last_torrents(self, category=None, subcategory=None, limit=25):
        """Get the last torrents, optionally filtered by category or subcategory."""
        params = {}
        if category:
            params["category"] = category
        if subcategory:
            params["subcategory"] = subcategory
        if limit and 1 <= limit <= 25:
            params["limit"] = limit
        return self._make_request("GET", "last-torrents", params=params)

    def search(self, query, category=None, subcategory=None):
        """Search for torrents, optionally filtered by category or subcategory."""
        params = {"name": query}
        if category:
            params["category"] = category
        if subcategory:
            params["subcategory"] = subcategory
        return self._make_request("GET", "search", params=params)

    def get_video_torrents(self, limit=25):
        """Get the last video torrents."""
        return self.get_last_torrents(category=1, limit=limit)

    def get_audio_torrents(self, limit=25):
        """Get the last audio torrents."""
        return self.get_last_torrents(category=2, limit=limit)

    def get_application_torrents(self, limit=25):
        """Get the last application torrents."""
        return self.get_last_torrents(category=3, limit=limit)

    def get_ebook_torrents(self, limit=25):
        """Get the last ebook torrents."""
        return self.get_last_torrents(category=4, limit=limit)

    def get_game_torrents(self, limit=25):
        """Get the last game torrents."""
        return self.get_last_torrents(category=5, limit=limit)

    def get_training_torrents(self, limit=25):
        """Get the last training torrents."""
        return self.get_last_torrents(category=6, limit=limit)

    def get_adult_torrents(self, limit=25):
        """Get the last adult torrents."""
        return self.get_last_torrents(category=7, limit=limit)

    @RateLimiter()
    def download_torrent(self, torrent_id):
        """Download a specific torrent file."""
        url = f"{self.base_url}/{self.sharewood_passkey}/{torrent_id}/download"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while downloading the torrent: {e}")
            raise

    def __del__(self):
        """Close the session when the object is destroyed."""
        self.session.close()
