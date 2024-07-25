from typing import Union, Literal, Optional, List, Tuple
from urllib.parse import urlencode

import orjson
import requests

from .response_models import (
    SessionsListResponse,
    SesssionCreateResponse,
    FlareSolverOK,
    GetPostRequestResponse,
)
from .solver_exceptions import UnsupportedProxySchema, FlareSolverError


def _check_proxy_url(proxy_url: str) -> None:
    if (
        not proxy_url.startswith("http://")
        and not proxy_url.startswith("https://")
        and not proxy_url.startswith("socks4://")
        and not proxy_url.startswith("socks5://")
    ):
        raise UnsupportedProxySchema(
            f"Supported proxy schemas: ['http(s), socks4, socks5']. Yours: {proxy_url.split('://', 1)[0]}"
        )


class FlareSolverr:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: Optional[Union[str, int]] = "8191",
        http_schema: Literal["http", "https"] = "http",
        additional_headers: dict = None,
        v: str = "v1",
    ) -> None:
        """
        :param host: Host address for FlareSolverr. Default: localhost.
        :type host: str
        :param port:  Host port for FlareSolverr. Defaul: 8191.
        :type port: str | int
        :param http_schema: Http schema for the requests module. Default: http
        :type http_schema: Literal["http", "https"]
        :param additional_headers: Additional headers you want to include while sending requests to FlareSolverr.
        :type additional_headers: dict
        :param v: FlareSolverr endpoint version. Do not change until strictly necessary.
        :type v: str
        """
        self.req_session = requests.Session()
        ah = additional_headers if additional_headers is not None else {}
        self.req_session.headers.update = {"Content-Type": "application/json", **ah}

        self.host = host
        self.port = str(port) if port is not None else None
        self.http_schema = http_schema
        self.v = v
        self.flare_solverr_url = (
            f"{http_schema}://{host}{':' + self.port if port is not None else ''}"
        )
        self.version, self.user_agent = self._check_flare_solver()
        self.flare_solverr_url = (
            f"{http_schema}://{host}{':' + self.port if port is not None else ''}/{v}"
        )

    def _check_flare_solver(self) -> Tuple[str, str]:
        response = self.req_session.get(self.flare_solverr_url)
        resp_dict = orjson.loads(response.content)
        return resp_dict["version"], resp_dict["userAgent"]

    @property
    def sessions(self) -> List[str]:
        """
        Get session ids as a list.
        :rtype: List[str]
        :return: All session ids as a list
        """
        payload = {"cmd": "sessions.list"}
        response = self.req_session.post(self.flare_solverr_url, json=payload)
        response_dict = orjson.loads(response.content)

        if response_dict["status"] != "ok":
            raise FlareSolverError.from_dict(response_dict)
        return SessionsListResponse.from_dict(response_dict).sessions

    @property
    def _sessions_raw(self) -> SessionsListResponse:
        """
        Get the whole response as SessionsListResponse object.
        :rtype: SessionsListResponse
        :return: A class containing OK messages and sessions as a list.
        """
        payload = {"cmd": "sessions.list"}
        response = self.req_session.post(self.flare_solverr_url, json=payload)
        response_dict = orjson.loads(response.content)

        if response_dict["status"] != "ok":
            raise FlareSolverError.from_dict(response_dict)
        return SessionsListResponse.from_dict(response_dict)

    def create_session(
        self, session_id: str = None, proxy_url: str = None
    ) -> SesssionCreateResponse:
        """
        Create a session. This will launch a new browser instance which will retain cookies.
        :param session_id: String. Optional.
        :param proxy_url: String. Optional. Must include proxy schema. ("http://", "socks4://", "socks5://")
        :type session_id: str
        :type proxy_url: str
        :rtype: SesssionCreateResponse
        :return: FlareSolverr sessions.create response as a class.
        """
        payload = {
            "cmd": "sessions.create",
        }
        if session_id:
            payload["session"] = session_id
        if proxy_url:
            _check_proxy_url(proxy_url)
            payload["proxy"] = {"url": proxy_url}
        response = self.req_session.post(self.flare_solverr_url, json=payload)
        response_dict = orjson.loads(response.content)

        if response_dict["status"] != "ok":
            raise FlareSolverError.from_dict(response_dict)
        return SesssionCreateResponse.from_dict(response_dict)

    def destroy_session(self, session_id: str) -> FlareSolverOK:
        """
        Destroy an existing FlareSolverr session.
        :param session_id: Required. String.
        :type session_id: str
        :rtype: FlareSolverOK
        :return: Class containing OK message.
        """
        payload = {"cmd": "sessions.destroy", "session": session_id}

        response = self.req_session.post(self.flare_solverr_url, json=payload)
        response_dict = orjson.loads(response.content)

        if response_dict["status"] != "ok":
            raise FlareSolverError.from_dict(response_dict)
        return FlareSolverOK.from_dict(response_dict)

    def _do_the_work_for_get_post(
        self, payload: dict, session, session_ttl_minutes, cookies, proxy_url
    ) -> GetPostRequestResponse:
        if session:
            payload["session"] = session
        if session_ttl_minutes:
            payload["session_ttl_minutes"] = session_ttl_minutes
        if cookies:
            payload["cookies"] = cookies
        if proxy_url:
            _check_proxy_url(proxy_url)
            payload["proxy"] = {"url": proxy_url}

        response = self.req_session.post(self.flare_solverr_url, json=payload)
        response_dict = orjson.loads(response.content)

        if response_dict["status"] != "ok":
            raise FlareSolverError.from_dict(response_dict)
        return GetPostRequestResponse.from_dict(response_dict)

    def request_get(
        self,
        url: str,
        session: Optional[str] = None,
        session_ttl_minutes: Optional[int] = None,
        max_timeout: int = 60000,
        cookies: Optional[List[dict]] = None,
        return_only_cookies: bool = False,
        proxy_url: Optional[str] = None,
    ) -> GetPostRequestResponse:
        """
        :param url: (required) str.
        :type url: str
        :param session: (optional) str. Session id for the request.
        :type session: str
        :param session_ttl_minutes: (optional) int. FlareSolverr will automatically rotate expired sessions based on the TTL provided in minutes.
        :type session_ttl_minutes: int
        :param max_timeout: (optional) int, default: 60000. Max timeout to solve the challenge in milliseconds.
        :type max_timeout: int
        :param cookies: (optional) dict. Additional cookes to be used by the browser.
        :type cookies: dict
        :param return_only_cookies: (optional) bool, default: False. Only returns the cookies.
        :type return_only_cookies: bool
        :param proxy_url: (optional) str. Proxy url.
        :type proxy_url: str
        :rtype: GetPostRequestResponse
        :return: A class containing website data and other related request data.
        """
        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": max_timeout,
            "returnOnlyCookies": return_only_cookies,
        }
        return self._do_the_work_for_get_post(
            payload, session, session_ttl_minutes, cookies, proxy_url
        )

    def request_post(
        self,
        url: str,
        post_data: dict,
        session: Optional[str] = None,
        session_ttl_minutes: Optional[int] = None,
        max_timeout: int = 60000,
        cookies: Optional[List[dict]] = None,
        return_only_cookies: bool = False,
        proxy_url: Optional[str] = None,
    ) -> GetPostRequestResponse:
        """
        :param url: (required) str.
        :type url: str
        :param post_data: (required) str. Data to post as a dictionary. Automatically converted to x-www-form-urlencoded.
        :type post_data: dict
        :param session: (optional) str. Session id for the request.
        :type session: str
        :param session_ttl_minutes: (optional) int. FlareSolverr will automatically rotate expired sessions based on the TTL provided in minutes.
        :type session_ttl_minutes: int
        :param max_timeout: (optional) int, default: 60000. Max timeout to solve the challenge in milliseconds.
        :type max_timeout: int
        :param cookies: (optional) dict. Additional cookes to be used by the browser.
        :type cookies: dict
        :param return_only_cookies: (optional) bool, default: False. Only returns the cookies.
        :type return_only_cookies: bool
        :param proxy_url: (optional) str. Proxy url.
        :type proxy_url: str
        :rtype: GetPostRequestResponse
        :return: A class containing website data and other related request data.
        """
        payload = {
            "cmd": "request.post",
            "url": url,
            "maxTimeout": max_timeout,
            "returnOnlyCookies": return_only_cookies,
            "postData": urlencode(post_data),
        }
        return self._do_the_work_for_get_post(
            payload, session, session_ttl_minutes, cookies, proxy_url
        )
