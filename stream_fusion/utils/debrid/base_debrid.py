from collections import deque
import json
import time

import requests

from stream_fusion.logging_config import logger
from stream_fusion.settings import settings


class BaseDebrid:
    def __init__(self, config):
        self.config = config
        self.logger = logger
        self.__session = self._create_session()

        # Rate limiters
        self.global_limit = 250
        self.global_period = 60
        self.torrent_limit = 1
        self.torrent_period = 1

        self.global_requests = deque()
        self.torrent_requests = deque()

    def _create_session(self):
        session = requests.Session()
        if settings.proxy_url:
            self.logger.info(f"BaseDebrid: Using proxy: {settings.proxy_url}")
            session.proxies = {
                "http": str(settings.proxy_url),
                "https": str(settings.proxy_url),
            }
        return session

    def _rate_limit(self, requests_queue, limit, period):
        current_time = time.time()

        while requests_queue and requests_queue[0] <= current_time - period:
            requests_queue.popleft()

        if len(requests_queue) >= limit:
            sleep_time = requests_queue[0] - (current_time - period)
            if sleep_time > 0:
                time.sleep(sleep_time)

        requests_queue.append(time.time())

    def _global_rate_limit(self):
        self._rate_limit(self.global_requests, self.global_limit, self.global_period)

    def _torrent_rate_limit(self):
        self._rate_limit(self.torrent_requests, self.torrent_limit, self.torrent_period)

    def json_response(self, url, method="get", data=None, headers=None, files=None):
        self._global_rate_limit()
        if "torrents" in url:
            self._torrent_rate_limit()

        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                if method == "get":
                    response = self.__session.get(url, headers=headers)
                elif method == "post":
                    response = self.__session.post(
                        url, data=data, headers=headers, files=files
                    )
                elif method == "put":
                    response = self.__session.put(url, data=data, headers=headers)
                elif method == "delete":
                    response = self.__session.delete(url, headers=headers)
                else:
                    raise ValueError(f"BaseDebrid: Unsupported HTTP method: {method}")

                response.raise_for_status()

                try:
                    return response.json()
                except json.JSONDecodeError as json_err:
                    self.logger.error(f"BaseDebrid: Invalid JSON response: {json_err}")
                    self.logger.debug(
                        f"BaseDebrid: Response content: {response.text[:200]}..."
                    )
                    if attempt < max_attempts - 1:
                        wait_time = 2**attempt + 1
                        self.logger.info(
                            f"BaseDebrid: Retrying in {wait_time} seconds..."
                        )
                        time.sleep(wait_time)
                    else:
                        return None

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 429:
                    wait_time = 2**attempt + 1
                    self.logger.warning(
                        f"BaseDebrid: Rate limit exceeded. Attempt {attempt + 1}/{max_attempts}. Waiting for {wait_time} seconds."
                    )
                    time.sleep(wait_time)
                elif 400 <= status_code < 500:
                    self.logger.error(
                        f"BaseDebrid: Client error occurred: {e}. Status code: {status_code}"
                    )
                    return None
                elif 500 <= status_code < 600:
                    self.logger.error(
                        f"BaseDebrid: Server error occurred: {e}. Status code: {status_code}"
                    )
                    if attempt < max_attempts - 1:
                        wait_time = 2**attempt + 1
                        self.logger.info(
                            f"BaseDebrid: Retrying in {wait_time} seconds..."
                        )
                        time.sleep(wait_time)
                    else:
                        return None
                else:
                    self.logger.error(
                        f"BaseDebrid: Unexpected HTTP error occurred: {e}. Status code: {status_code}"
                    )
                    return None
            except requests.exceptions.ConnectionError as e:
                self.logger.error(f"BaseDebrid: Connection error occurred: {e}")
                if attempt < max_attempts - 1:
                    wait_time = 2**attempt + 1
                    self.logger.info(f"BaseDebrid: Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return None
            except requests.exceptions.Timeout as e:
                self.logger.error(f"BaseDebrid: Request timed out: {e}")
                if attempt < max_attempts - 1:
                    wait_time = 2**attempt + 1
                    self.logger.info(f"BaseDebrid: Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return None
            except requests.exceptions.RequestException as e:
                self.logger.error(f"BaseDebrid: An unexpected error occurred: {e}")
                return None

        self.logger.error(
            "BaseDebrid: Max attempts reached. Unable to complete request."
        )
        return None

    def wait_for_ready_status(self, check_status_func, timeout=30, interval=5):
        self.logger.info(f"BaseDebrid: Waiting for {timeout} seconds for caching.")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if check_status_func():
                self.logger.info("BaseDebrid: File is ready!")
                return True
            time.sleep(interval)
        self.logger.info(f"BaseDebrid: Waiting timed out.")
        return False

    def download_torrent_file(self, download_url):
        response = requests.get(download_url)
        response.raise_for_status()
        return response.content

    def get_stream_link(self, query, ip=None):
        raise NotImplementedError
    
    def add_magnet_or_torrent(self, magnet, torrent_download=None, ip=None):
        raise NotImplementedError

    def add_magnet(self, magnet, ip=None):
        raise NotImplementedError

    def get_availability_bulk(self, hashes_or_magnets, ip=None):
        raise NotImplementedError
