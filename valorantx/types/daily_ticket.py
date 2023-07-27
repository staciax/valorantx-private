from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


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
    RewardGrants: NotRequired[Optional[Any]]  # not sure


class DailyTicket(TypedDict):
    Version: int
    DailyRewards: DailyRewards
    ProcessedMatches: List[ProcessedMatch]
