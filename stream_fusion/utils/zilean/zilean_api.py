import requests
from typing import List, Optional
from pydantic import BaseModel, Field
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from stream_fusion.settings import settings
from stream_fusion.logging_config import logger


class DmmQueryRequest(BaseModel):
    queryText: Optional[str] = None


class TorrentInfo(BaseModel):
    resolution: Optional[str] = None
    year: Optional[int] = None
    remastered: bool = False
    source: Optional[str] = None
    codec: Optional[str] = None
    group: Optional[str] = None
    episodes: Optional[List[int]] = Field(default_factory=list)
    seasons: Optional[List[int]] = Field(default_factory=list)
    languages: Optional[List[str]] = Field(default_factory=list)
    title: Optional[str] = None
    rawTitle: Optional[str] = None
    size: int = 0
    infoHash: Optional[str] = None
    isPossibleMovie: bool = False


class ExtractedDmmEntry(BaseModel):
    filename: str
    infoHash: str
    filesize: int
    parseResponse: Optional[TorrentInfo] = None


class ImdbFile(BaseModel):
    imdbId: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    adult: bool = False
    year: int = 0


class ZileanAPI:
    def __init__(
        self,
        pool_connections: int = settings.zilean_pool_connections,
        pool_maxsize: int = settings.zilean_api_pool_maxsize,
        max_retries: int = settings.zilean_max_retry,
    ):
        self.base_url = settings.zilean_url
        if not self.base_url:
            logger.error("Zilean API URL is not set in the environment variables.")
            raise ValueError("Zilean API URL is not set in the environment variables.")
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers.update(
            {"accept": "application/json", "Content-Type": "application/json"}
        )
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête API : {e}")
            raise

    def dmm_search(self, query: DmmQueryRequest) -> List[ExtractedDmmEntry]:
        response = self._request("POST", "/dmm/search", json=query.dict())
        return [ExtractedDmmEntry(**entry) for entry in response.json()]

    def dmm_filtered(
        self,
        query: Optional[str] = None,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        year: Optional[int] = None,
        language: Optional[str] = None,
        resolution: Optional[str] = None,
    ) -> List[ExtractedDmmEntry]:
        params = {
            "Query": query,
            "Season": season,
            "Episode": episode,
            "Year": year,
            "Language": language,
            "Resolution": resolution,
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._request("GET", "/dmm/filtered", params=params)
        return [ExtractedDmmEntry(**entry) for entry in response.json()]

    def dmm_on_demand_scrape(self) -> None:
        self._request("GET", "/dmm/on-demand-scrape")

    def healthchecks_ping(self) -> str:
        response = self._request("GET", "/healthchecks/ping")
        return response.text

    def imdb_search(
        self, query: Optional[str] = None, year: Optional[int] = None
    ) -> List[ImdbFile]:
        params = {"Query": query, "Year": year}
        params = {k: v for k, v in params.items() if v is not None}
        response = self._request("POST", "/imdb/search", params=params)
        return [ImdbFile(**file) for file in response.json()]

    def __del__(self):
        self.session.close()
