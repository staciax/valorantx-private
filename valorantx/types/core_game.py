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

from typing import TYPE_CHECKING, Any, List, Mapping, Optional, TypedDict, Union

if TYPE_CHECKING:
    import datetime

    from .player import PlayerIdentity


class SeasonalBadgeInfo(TypedDict):
    SeasonID: str
    NumberOfWins: int
    WinsByTier: Optional[Any]
    Rank: int
    LeaderboardRank: int


class ConnectionDetails(TypedDict):
    GameServerHosts: List[str]
    GameServerHost: str
    GameServerPort: int
    GameServerObfuscatedIP: int
    GameClientHash: int
    PlayerKey: int


class CoreGamePlayer(TypedDict):
    Subject: str
    MatchID: str
    Version: int


class PlayerCoreGame(TypedDict):
    Subject: str
    CharacterID: str
    CharacterSelectionState: str
    PlayerIdentity: PlayerIdentity
    SeasonalBadgeInfo: SeasonalBadgeInfo
    IsCoach: bool
    IsAssociated: bool


class PreGameMatch(TypedDict):
    MatchID: str
    Version: int
    State: str
    MapID: str
    ModeID: str
    ProvisioningFlow: str
    GamePodID: str
    AllMUCName: str
    TeamMUCName: str
    TeamVoiceID: str
    IsReconnectable: bool
    ConnectionDetails: ConnectionDetails
    PostGameDetails: Optional[Any]
    Players: List[PlayerCoreGame]
    MatchmakingData: Optional[Any]
