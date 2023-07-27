from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from ..types.daily_ticket import (
        DailyRewards as DailyRewardsPayload,
        DailyTicket as DailyTicketPayload,
        Milestone as MilestonePayload,
        ProcessedMatch as ProcessedMatchPayload,
    )
    from .match import MatchDetails

__all__ = (
    'DailyTicket',
    'DailyRewards',
    'Milestone',
    'DailyTicketProcessedMatch',
)


class Milestone:
    def __init__(self, data: MilestonePayload) -> None:
        self.progress: int = data['Progress']
        self.bonus_applied: bool = data['BonusApplied']

    def __repr__(self) -> str:
        return f'<Milestone progress={self.progress} bonus_applied={self.bonus_applied}>'


class DailyRewards:
    def __init__(self, data: DailyRewardsPayload) -> None:
        self._remaining_lifetime_seconds: int = data['RemainingLifetimeSeconds']
        self.bonus_milestones_pending: int = data['BonusMilestonesPending']
        self.milestones: List[Milestone] = [Milestone(milestone) for milestone in data['Milestones']]

    def __repr__(self) -> str:
        return f'<DailyRewards remaining_lifetime={self.remaining_lifetime} bonus_milestones_pending={self.bonus_milestones_pending} milestones={self.milestones}>'

    @property
    def remaining_lifetime(self) -> datetime.datetime:
        return datetime.datetime.now() + datetime.timedelta(seconds=self._remaining_lifetime_seconds)


class ProcessedMatch:
    def __init__(self, client: Client, data: ProcessedMatchPayload) -> None:
        self._client: Client = client
        self.id: str = data['ID']
        self.progress_before: int = data['ProgressBefore']
        self.progress_after: int = data['ProgressAfter']
        self.xp: int = data['XP']
        self.soft_currency: int = data['SoftCurrency']
        self.was_penalized: bool = data['WasPenalized']
        self.bonuses_applied: int = data['BonusesApplied']
        self.daily_bonus_state: List[bool] = data['DailyBonusState']
        self.reward_grants: Optional[Any] = data.get('RewardGrants')

    def __repr__(self) -> str:
        return f'<ProcessedMatch id={self.id} progress_before={self.progress_before} progress_after={self.progress_after} xp={self.xp} soft_currency={self.soft_currency} was_penalized={self.was_penalized} bonuses_applied={self.bonuses_applied} daily_bonus_state={self.daily_bonus_state} reward_grants={self.reward_grants}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProcessedMatch) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    async def fetch_match_details(self) -> MatchDetails:
        return await self._client.fetch_match_details(self.id)


class DailyTicket:
    def __init__(self, client: Client, data: DailyTicketPayload) -> None:
        self._client: Client = client
        self._update(data)

    def _update(self, data: DailyTicketPayload) -> None:
        self.version: int = data['Version']
        self.daily_rewards: DailyRewards = DailyRewards(data['DailyRewards'])
        self.processed_matches: List[ProcessedMatch] = [
            ProcessedMatch(self._client, match) for match in data['ProcessedMatches']
        ]

    def __repr__(self) -> str:
        return f'<DailyTicket version={self.version} daily_rewards={self.daily_rewards}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DailyTicket) and self.version == other.version

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.version)

    async def renew(self) -> Self:
        data = await self._client.http.post_daily_ticket()
        self._update(data)
        return self


DailyTicketProcessedMatch = ProcessedMatch
