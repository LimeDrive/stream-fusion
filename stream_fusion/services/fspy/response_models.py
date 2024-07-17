from dataclasses import dataclass
from typing import List


@dataclass
class FlareSolverOK:
    startTimestamp: int
    endTimestamp: int
    version: str
    status: str
    message: str

    @classmethod
    def from_dict(cls, dct):
        return cls(
            dct["startTimestamp"],
            dct["endTimestamp"],
            dct["version"],
            dct["status"],
            dct["message"]
        )


@dataclass
class SessionsListResponse:
    startTimestamp: int
    endTimestamp: int
    version: str
    status: str
    message: str
    sessions: List[str]

    @classmethod
    def from_dict(cls, dct):
        return cls(
            dct["startTimestamp"],
            dct["endTimestamp"],
            dct["version"],
            dct["status"],
            dct["message"],
            dct["sessions"]
        )


@dataclass
class SesssionCreateResponse:
    startTimestamp: int
    endTimestamp: int
    version: str
    status: str
    message: str
    session: str

    @classmethod
    def from_dict(cls, dct):
        return cls(
            dct["startTimestamp"],
            dct["endTimestamp"],
            dct["version"],
            dct["status"],
            dct["message"],
            dct["session"]
        )


@dataclass
class Solution:
    url: str
    status: int
    cookies: dict
    user_agent: str
    headers: dict
    response: str

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(
            dct["url"],
            dct["status"],
            dct["cookies"],
            dct["userAgent"],
            dct["headers"],
            dct["response"]
        )


@dataclass
class GetPostRequestResponse:
    startTimestamp: int
    endTimestamp: int
    version: str
    status: str
    message: str
    solution: Solution

    @classmethod
    def from_dict(cls, dct: dict):
        return cls(
            dct["startTimestamp"],
            dct["endTimestamp"],
            dct["version"],
            dct["status"],
            dct["message"],
            Solution.from_dict(dct["solution"])
        )
