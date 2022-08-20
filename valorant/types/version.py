from __future__ import annotations

from .base import AssetPayload
from typing import TypedDict

class VersionData(TypedDict):
    manifestId: str
    branch: str
    version: str
    buildVersion: str
    engineVersion: str
    riotClientVersion: str
    buildDate: str

class Version(AssetPayload):
    data: VersionData
