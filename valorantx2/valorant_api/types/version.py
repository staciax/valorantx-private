from typing import TypedDict

from .response import Response


class Version(TypedDict):
    manifestId: str
    branch: str
    version: str
    buildVersion: str
    engineVersion: str
    riotClientVersion: str
    riotClientBuild: str
    buildDate: str


Data = Response[Version]
