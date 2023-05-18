from __future__ import annotations

from typing import List, TypedDict


class Progress(TypedDict):
    Level: int
    XP: int


class XPSource(TypedDict):
    ID: str
    Amount: int


class XPMultiplier(TypedDict):
    ID: str
    Value: int


class History(TypedDict):
    ID: str
    MatchStart: str
    StartProgress: Progress
    EndProgress: Progress
    XPDelta: int
    XPSources: List[XPSource]
    XPMultipliers: List[XPMultiplier]


class AccountXP(TypedDict):
    Version: int
    Subject: str
    Progress: Progress
    History: List[History]
    LastTimeGrantedFirstWin: str
    NextTimeFirstWinAvailable: str
