from collections import deque
import time

import requests

from stream_fusion.logging_config import logger
from stream_fusion.settings import settings
from stream_fusion.services.ygg_conn import YggSessionManager


class BaseDebrid:
    def __init__(self, config):
        self.config = config
        self.logger = logger
        self.__session = requests.Session()
        self.__ygg_session_manager = YggSessionManager(config)
        
        # Limiteurs de débit
        self.global_limit = 250
        self.global_period = 60
        self.torrent_limit = 1
        self.torrent_period = 1
        
        self.global_requests = deque()
        self.torrent_requests = deque()

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

    def get_json_response(self, url, method='get', data=None, headers=None, files=None):
        self._global_rate_limit()
        
        if 'torrents' in url:
            self._torrent_rate_limit()
        
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                if method == 'get':
                    response = self.__session.get(url, headers=headers)
                elif method == 'post':
                    response = self.__session.post(url, data=data, headers=headers, files=files)
                elif method == 'put':
                    response = self.__session.put(url, data=data, headers=headers)
                elif method == 'delete':
                    response = self.__session.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    wait_time = 2 ** attempt + 1
                    self.logger.warning(f"Rate limit exceeded. Attempt {attempt + 1}/{max_attempts}. Waiting for {wait_time} seconds.")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"HTTP error occurred: {e}")
                    return None
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
                return None

        self.logger.error("Max attempts reached. Unable to complete request.")
        return None

    def wait_for_ready_status(self, check_status_func, timeout=30, interval=5):
        self.logger.info(f"Waiting for {timeout} seconds to cache.")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if check_status_func():
                self.logger.info("File is ready!")
                return True
            time.sleep(interval)
        self.logger.info(f"Waiting timed out.")
        return False

    def donwload_torrent_file(self, download_url):
        if download_url.startswith(settings.ygg_url):
            ygg_session = self.__ygg_session_manager.get_or_create_session()
            response = ygg_session.get(download_url)
            response.raise_for_status()
        elif download_url.startswith(settings.ygg_proxy_url):
            headers = {'accept': 'application/json',
                       'api-key': settings.ygg_proxy_apikey}
            response = requests.get(download_url, headers=headers)
            response.raise_for_status()
        else:
            response = requests.get(download_url)
            response.raise_for_status()

        return response.content

    def get_stream_link(self, query, ip=None):
        raise NotImplementedError

    def add_magnet(self, magnet, ip=None):
        raise NotImplementedError

    def get_availability_bulk(self, hashes_or_magnets, ip=None):
        raise NotImplementedError
