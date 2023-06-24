from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class PlatformInfo(TypedDict):
    platformType: str
    platformOS: str
    platformOSVersion: str
    platformChipset: str


class Player(TypedDict):
    Subject: str
    Version: int
    CurrentPartyID: str
    Invites: Optional[Any]
    Requests: List[Any]
    PlatformInfo: PlatformInfo


class PlayerIdentity(TypedDict):
    Subject: str
    PlayerCardID: str
    PlayerTitleID: str
    AccountLevel: int
    PreferredLevelBorderID: str
    Incognito: bool
    HideAccountLevel: bool


class Ping(TypedDict):
    Ping: int
    GamePodID: str


class Member(TypedDict):
    Subject: str
    CompetitiveTier: int
    PlayerIdentity: PlayerIdentity
    SeasonalBadgeInfo: Optional[Any]
    IsOwner: bool
    QueueEligibleRemainingAccountLevels: int
    Pings: List[Ping]
    IsReady: bool
    IsModerator: bool
    UseBroadcastHUD: bool
    PlatformType: str


class CustomGameRules(TypedDict):
    AllowGameModifiers: NotRequired[str]
    IsOvertimeWinByTwo: NotRequired[str]
    PlayOutAllRounds: NotRequired[str]
    SkipMatchHistory: NotRequired[str]
    TournamentMode: NotRequired[str]


class CustomGameSettings(TypedDict):
    Map: str
    Mode: str
    UseBots: bool
    GamePod: str
    GameRules: Optional[CustomGameRules]  # not sure if this is correct


class CustomGameMembership(TypedDict):
    teamOne: Optional[Any]
    teamTwo: Optional[Any]
    teamSpectate: Optional[Any]
    teamOneCoaches: Optional[Any]
    teamTwoCoaches: Optional[Any]


class CustomGameData(TypedDict):
    Settings: CustomGameSettings
    Membership: CustomGameMembership
    MaxPartySize: int
    AutobalanceEnabled: bool
    AutobalanceMinPlayers: int
    HasRecoveryData: bool


class MatchmakingData(TypedDict):
    QueueID: str
    PreferredGamePods: List[str]
    SkillDisparityRRPenalty: int


class Invite(TypedDict):
    ID: str
    PartyID: str
    Subject: str
    InvitedBySubject: str
    CreatedAt: str
    RefreshedAt: str
    ExpiresIn: int


class Request(TypedDict):
    ID: str
    PartyID: str
    RequestedBySubject: str
    Subjects: List[str]
    CreatedAt: str
    RequestedAt: str
    RefreshedAt: str
    ExpiresIn: int


class CheatData(TypedDict):
    GamePodOverride: str
    ForcePostGameProcessing: bool


class Party(TypedDict):
    ID: str
    MUCName: str
    VoiceRoomID: str
    Version: int
    ClientVersion: str
    Members: Optional[List[Member]]
    State: str  # Literal ...
    PreviousState: str
    StateTransitionReason: str
    Accessibility: str
    CustomGameData: CustomGameData
    MatchmakingData: MatchmakingData
    Invites: Optional[List[Invite]]
    Requests: Optional[List[Request]]
    QueueEntryTime: str
    ErrorNotification: str
    RestrictedSeconds: int
    EligibleQueues: List[str]
    QueueIneligibilities: Optional[List[Any]]
    CheatData: CheatData
    XPBonuses: Optional[List[Any]]
