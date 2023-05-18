from typing import TypedDict

from .response import Response


class Version_(TypedDict):
    manifestId: str
    branch: str
    version: str
    buildVersion: str
    engineVersion: str
    riotClientVersion: str
    riotClientBuild: str
    buildDate: str


Version = Response[Version_]
