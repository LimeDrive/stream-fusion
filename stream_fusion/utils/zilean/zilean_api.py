import requests

from typing import List, Optional
from dataclasses import dataclass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from stream_fusion.settings import settings
from stream_fusion.logging_config import logger

@dataclass
class DmmQueryRequest:
    queryText: Optional[str] = None

@dataclass
class TorrentInfo:
    resolution: Optional[str] = None
    year: Optional[int] = None
    remastered: bool = False
    source: Optional[str] = None
    codec: Optional[str] = None
    group: Optional[str] = None
    episodes: Optional[List[int]] = None
    seasons: Optional[List[int]] = None
    languages: Optional[List[str]] = None
    title: Optional[str] = None
    rawTitle: Optional[str] = None
    size: int = 0
    infoHash: Optional[str] = None
    isPossibleMovie: bool = False

@dataclass
class ExtractedDmmEntry:
    filename: Optional[str] = None
    infoHash: Optional[str] = None
    filesize: int = 0
    parseResponse: TorrentInfo = TorrentInfo()

@dataclass
class ImdbFile:
    imdbId: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    adult: bool = False
    year: int = 0

class ZileanAPI:
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 10, max_retries: int = 3):
        self.base_url = settings.zilean_url
        self.session = requests.Session()
        
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=Retry(total=max_retries, backoff_factor=0.1)
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def dmm_search(self, query: DmmQueryRequest) -> List[ExtractedDmmEntry]:
        response = self._request('POST', '/dmm/search', json=query.__dict__)
        return [ExtractedDmmEntry(**entry) for entry in response.json()]

    def dmm_filtered(self, query: Optional[str] = None, season: Optional[int] = None,
                     episode: Optional[int] = None, year: Optional[int] = None,
                     language: Optional[str] = None, resolution: Optional[str] = None) -> List[ExtractedDmmEntry]:
        params = {
            "Query": query,
            "Season": season,
            "Episode": episode,
            "Year": year,
            "Language": language,
            "Resolution": resolution
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._request('GET', '/dmm/filtered', params=params)
        return [ExtractedDmmEntry(**entry) for entry in response.json()]

    def dmm_on_demand_scrape(self) -> None:
        self._request('GET', '/dmm/on-demand-scrape')

    def healthchecks_ping(self) -> str:
        response = self._request('GET', '/healthchecks/ping')
        return response.text

    def imdb_search(self, query: Optional[str] = None, year: Optional[int] = None) -> List[ImdbFile]:
        params = {
            "Query": query,
            "Year": year
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._request('POST', '/imdb/search', params=params)
        return [ImdbFile(**file) for file in response.json()]

    def __del__(self):
        self.session.close()