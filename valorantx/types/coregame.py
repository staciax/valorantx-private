from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from .party import PlayerIdentity


class Player(TypedDict):
    Subject: str
    MatchID: str
    Version: int


class MatchmakingData(TypedDict):
    QueueID: str
    IsRanked: bool


class ConnectionDetails(TypedDict):
    GameServerHosts: List[str]
    GameServerHost: str
    GameServerPort: int
    GameServerObfuscatedIP: str
    GameClientHash: str
    PlayerKey: str


class SeasonalBadgeInfo(TypedDict):
    SeasonID: Union[str, Literal['']]
    NumberOfWins: int
    WinsByTier: Optional[Any]
    Rank: int
    LeaderboardRank: int


class MatchPlayer(TypedDict):
    Subject: str
    TeamID: Union[str, Literal['Blue', 'Red']]
    CharacterID: str
    PlayerIdentity: PlayerIdentity
    SeasonalBadgeInfo: SeasonalBadgeInfo
    IsCoach: bool
    IsAssociated: bool


class Match(TypedDict):
    MatchID: str
    Version: int
    State: Literal['IN_PROGRESS']
    MapID: str
    ModeID: str
    ProvisioningFlow: Literal['Matchmaking', 'CustomGame']
    GamePodID: str
    AllMUCName: str
    TeamMUCName: str
    TeamVoiceID: str
    IsReconnectable: bool
    ConnectionDetails: ConnectionDetails
    PostGameDetails: Optional[Any]
    Players: List[MatchPlayer]
    MatchmakingData: Optional[MatchmakingData]


class SocketItem(TypedDict):
    ID: str
    TypeID: str


class Socket(TypedDict):
    ID: str
    Item: SocketItem


class SpraySelection(TypedDict):
    SocketID: str
    SprayID: str
    LevelID: str


class Item(TypedDict):
    ID: str
    TypeID: str
    Sockets: Dict[str, Socket]


class Sprays(TypedDict):
    SpraySelections: List[SpraySelection]


class Loadout(TypedDict):
    Sprays: Sprays
    Items: Dict[str, Item]


class LoadoutChild(TypedDict):
    CharacterID: str
    Loadout: Loadout


class Loaouts(TypedDict):
    Loadouts: List[LoadoutChild]
