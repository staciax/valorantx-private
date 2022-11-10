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

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, TypedDict, Union

if TYPE_CHECKING:
    import datetime

    from .player import PlayerIdentity


class PreGamePlayer(TypedDict):
    Subject: str
    MatchID: str
    Version: int


class SeasonalBadgeInfo(TypedDict):
    SeasonID: str
    NumberOfWins: int
    WinsByTier: Optional[Any]
    Rank: int
    LeaderboardRank: int


class PlayerPreGame(TypedDict):
    Subject: str
    CharacterID: str
    CharacterSelectionState: str
    CompetitiveTier: int
    PlayerIdentity: PlayerIdentity
    SeasonalBadgeInfo: SeasonalBadgeInfo
    IsCaptain: bool


class AllyTeam(TypedDict):
    TeamID: str
    Players: List[PlayerPreGame]


class PreGameMatch(TypedDict):
    ID: str
    Version: int
    Teams: List[Any]
    AllyTeam: AllyTeam
    EnemyTeam: Optional[Any]
    ObserverSubjects: List[Any]
    MatchCoaches: List[Any]
    EnemyTeamSize: int
    EnemyTeamLockCount: int
    PregameState: str
    LastUpdated: Union[str, datetime.datetime]
    MapID: str
    MapSelectPool: List[Any]
    BannedMapIDs: List[Any]
    CastedVotes: Dict[str, Any]  # TODO: not sure
    MapSelectSteps: int
    Team1: str
    GamePodID: str
    Mode: str
    VoiceSessionID: str
    MUCName: str
    QueueID: str
    ProvisioningFlowID: str
    IsRanked: bool
    PhaseTimeRemainingNS: int
    StepTimeRemainingNS: int
    altModesFlagADA: bool
    TournamentMetadata: Optional[Any]
    RosterMetadata: Optional[Any]
