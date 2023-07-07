from typing import Any, List, Optional, TypedDict


class Milestone(TypedDict):
    Progress: int
    BonusApplied: bool


class DailyRewards(TypedDict):
    RemainingLifetimeSeconds: int
    BonusMilestonesPending: int
    Milestones: List[Milestone]


class ProcessedMatch(TypedDict):
    ID: str
    ProgressBefore: int
    ProgressAfter: int
    XP: int
    SoftCurrency: int
    WasPenalized: bool
    BonusesApplied: int
    DailyBonusState: List[bool]
    RewardGrants: Optional[Any]


class DailyTicket(TypedDict):
    Version: int
    DailyRewards: DailyRewards
    ProcessedMatches: List[ProcessedMatch]
