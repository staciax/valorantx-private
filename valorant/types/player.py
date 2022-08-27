"""
The MIT License (MIT)

Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, TypedDict, Union

from valorant.types.match import (
    MatchPlayerPlatformInfo,
    MatchPlayerStats,
    RoundDamage,
    behaviorFactors,
    newPlayerExperienceDetails,
    xpModification,
)

if TYPE_CHECKING:
    import datetime


class PartialPlayer(TypedDict):
    puuid: str
    username: str
    tagline: str


class Player(PartialPlayer):
    region: str
    locale: Optional[str]


class AccountXPProgress(TypedDict):
    Level: int
    XP: int


class AccountXPSources(TypedDict):
    ID: str
    Amount: int


class AccountXPHistory(TypedDict):
    ID: str
    MatchStart: Union[str, datetime.datetime]
    StartProgress: AccountXPProgress
    EndProgress: AccountXPProgress
    XPSources: List[AccountXPSources]
    XPMultipliers: List[Any]


class AccountXP(TypedDict):
    Version: int
    Subject: str
    Progress: AccountXPProgress
    History: List[AccountXPHistory]
    LastTimeGrantedFirstWin: Union[str, datetime.datetime]
    NextTimeFirstWinAvailable: Union[str, datetime.datetime]


class PlayerMatch(Player):
    subject: str
    gameName: str
    tagLine: str
    platformInfo: MatchPlayerPlatformInfo
    teamId: str
    partyId: str
    characterId: str
    stats: MatchPlayerStats
    roundDamage: List[RoundDamage]
    competitiveTier: int
    playerCard: str
    playerTitle: str
    preferredLevelBorder: str
    accountLevel: int
    sessionPlaytimeMinutes: int
    xpModifications: List[xpModification]
    behaviorFactors: behaviorFactors
    newPlayerExperienceDetails: newPlayerExperienceDetails
