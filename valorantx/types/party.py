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

if TYPE_CHECKING:
    import datetime

    from .match import PlayerPlatformInfo
    from .player import PlayerIdentity


class PartyMember(TypedDict):
    Subject: str
    CompetitiveTier: int
    PlayerIdentity: PlayerIdentity
    SeasonalBadgeInfo: Any
    IsOwner: bool
    QueueEligibleRemainingAccountLevels: int
    Pings: List[Ping]
    IsReady: bool
    IsModerator: bool
    UseBroadcastHUD: bool
    PlatformType: str


class CustomSettings(TypedDict):
    Map: str
    Mode: str
    UseBots: bool
    GamePod: str
    GameRules: Optional[Any]


class CustomMembership(TypedDict):
    teamOne: Optional[Any]
    teamTwo: Optional[Any]
    teamSpectate: Optional[Any]
    teamOneCoaches: Optional[Any]
    teamTwoCoaches: Optional[Any]


class CustomGameData(TypedDict):
    Settings: CustomSettings
    Membership: CustomMembership
    MaxPartySize: int
    AutobalanceEnabled: bool
    AutobalanceMinPlayers: int


class Invite(TypedDict):
    ID: str
    PartyID: str
    Subject: str
    InvitedBySubject: str
    CreatedAt: Union[str, datetime.datetime]
    RefreshedAt: Union[str, datetime.datetime]
    ExpiresIn: int


class PartyPlayer(TypedDict):
    Subject: str
    Version: int
    CurrentPartyID: str
    Invites: Optional[List[Invite]]
    Requests: List[Any]
    PlatformInfo: PlayerPlatformInfo


class MatchmakingData(TypedDict):
    QueueID: str
    PreferredGamePods: List[str]
    SkillDisparityRRPenalty: int


class ErrorNotification(TypedDict):
    ErrorType: str
    ErroredPlayers: Optional[Any]


class CheatData(TypedDict):
    GamePodOverride: str
    ForcePostGameProcessing: bool


class Party(TypedDict):
    ID: str
    MUCName: str
    VoiceRoomID: str
    Version: int
    ClientVersion: str
    Members: List[PartyMember]
    State: str
    PreviousState: str
    StateTransitionReason: str
    Accessibility: str
    CustomGameData: CustomGameData
    MatchmakingData: MatchmakingData
    Invites: Optional[Any]
    Requests: List[Any]
    QueueEntryTime: Union[str, datetime.datetime]
    ErrorNotification: ErrorNotification
    RestrictedSeconds: int
    EligibleQueues: List[str]
    QueueIneligibilities: List[Any]
    CheatData: CheatData
    XPBonuses: List[Any]


class Ping(TypedDict):
    Ping: int
    GamePodID: str
