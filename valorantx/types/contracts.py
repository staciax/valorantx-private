from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class Reward(TypedDict):
    Amount: int
    Version: int


class ContractProgression(TypedDict):
    TotalProgressionEarned: int
    TotalProgressionEarnedVersion: int
    HighestRewardedLevel: Dict[str, Reward]


class Contract(TypedDict):
    ContractDefinitionID: str
    ContractProgression: ContractProgression
    ProgressionLevelReached: int
    ProgressionTowardsNextLevel: int


class Modifier(TypedDict):
    Value: int
    Name: Literal['RESTRICTIONS_XP', 'PREMIUM_CONTRACT_XP']
    BaseOnly: bool


# not sure https://valapidocs.techchrism.me/endpoint/contracts


class XPModifier(TypedDict):
    Value: int
    BaseMultiplierValue: int
    Modifiers: List[Modifier]


class XPGrant(TypedDict):
    GamePlayed: int
    GameWon: int
    RoundPlayed: int
    RoundWon: int
    Missions: Any
    Modifier: XPModifier
    NumAFKRounds: int


class ObjectiveDelta(TypedDict):
    ID: str
    ProgressBefore: int
    ProgressAfter: int


class MissionDelta(TypedDict):
    ID: str
    Objectives: Dict[str, int]
    ObjectiveDeltas: Dict[str, ObjectiveDelta]


class ContractDelta(TypedDict):
    ID: str
    TotalXPBefore: int
    TotalXPAfter: int


# end - not sure


class ProcessedMatch(TypedDict):
    ID: str
    StartTime: int
    XPGrants: Optional[XPGrant]
    RewardGrants: Optional[Dict[Any, Any]]  # unknown type
    MissionDeltas: Optional[Dict[str, MissionDelta]]
    ContractDeltas: Optional[Dict[str, ContractDelta]]
    CouldProgressMissions: bool


class Mission(TypedDict):
    ID: str
    Objectives: Dict[str, int]
    Complete: bool
    ExpirationTime: NotRequired[str]


class MissionMetadata(TypedDict):
    NPECompleted: NotRequired[bool]
    WeeklyCheckpoint: NotRequired[str]  # Date in ISO 8601 format
    WeeklyRefillTime: NotRequired[str]  # maybe not required i guess


class Contracts(TypedDict):
    Version: int
    Subject: str
    Contracts: List[Contract]
    ProcessedMatches: List[ProcessedMatch]
    ActiveSpecialContract: str  # is optional ?
    Missions: List[Mission]
    MissionMetadata: MissionMetadata
