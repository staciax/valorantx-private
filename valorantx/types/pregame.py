from typing import Any, List, Literal, Optional, TypedDict, Union

from .party import PlayerIdentity


class Player(TypedDict):
    Subject: str
    MatchID: str
    Version: int


class SeasonalBadgeInfo(TypedDict):
    SeasonID: Union[str, Literal['']]
    NumberOfWins: int
    WinsByTier: Optional[Any]
    Rank: int
    LeaderboardRank: int


class MatchPlayer(TypedDict):
    Subject: str
    CharacterID: str
    CharacterSelectionState: Literal['', 'selected' 'locked']
    PregamePlayerState: Literal['joined']
    CompetitiveTier: int
    PlayerIdentity: PlayerIdentity
    SeasonalBadgeInfo: SeasonalBadgeInfo
    IsCaptain: bool


class Team(TypedDict):
    TeamID: Union[str, Literal['Blue', 'Red']]
    Players: List[MatchPlayer]


class Match(TypedDict):
    ID: str
    Version: int
    Teams: List[Team]
    AllyTeam: Team
    EnemyTeam: Optional[Team]
    ObserverSubjects: List[Any]  # unknown type
    MatchCoaches: List[Any]  # unknown type
    EnemyTeamSize: int
    EnemyTeamLockCount: int
    PregameState: Literal['character_select_active', 'provisioned']
    LastUpdated: str
    MapID: str
    MapSelectPool: List[Any]
    BannedMapIDs: List[Any]
    CastedVotes: Any
    MapSelectSteps: List[Any]  # unknown type
    MapSelectStep: int
    Team1: str
    GamePodID: str
    Mode: str
    VoiceSessionID: str
    MUCName: str
    QueueID: str
    ProvisioningFlowID: Literal['Matchmaking', 'CustomGame']
    IsRanked: bool
    PhaseTimeRemainingNS: int
    StepTimeRemainingNS: int
    altModesFlagADA: bool
    TournamentMetadata: Optional[Any]
    RosterMetadata: Optional[Any]


class Spray(TypedDict):
    SpraySelections: Optional[Any]  # unknown type


class Loadout(TypedDict):
    Sprays: ...
    Items: Optional[Any]  # unknown type


class Loadouts(TypedDict):
    Loadouts: List[Any]
    LoadoutsValid: bool


# quite game 204, 404
