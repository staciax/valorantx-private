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

import datetime
import logging
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Mapping, Optional, Union

from .. import utils
from ..asset import Asset
from ..enums import ContractRewardType as RewardType, MissionType, RelationType, try_enum
from ..errors import InvalidContractType, InvalidRelationType
from ..localization import Localization
from .base import BaseModel
from .mission import MissionMeta, MissionU

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from ..types.contract import (
        Contract as ContractUPayload,
        Contracts as ContractsPayload,
        ProcessedMatch as ProcessedMatchPayload,
    )
    from .agent import Agent
    from .buddy import BuddyLevel
    from .currency import Currency
    from .event import Event
    from .player_card import PlayerCard
    from .player_title import PlayerTitle
    from .season import Season
    from .spray import Spray
    from .weapons import SkinLevel

__all__ = ('Contract', 'ContractU', 'Contracts')

_log = logging.getLogger(__name__)


class Contract(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Optional[Union[str, Dict[str, str]]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self._ship_it: bool = data.get('shipIt', False)
        self.free_reward_schedule_uuid: str = data['freeRewardScheduleUuid']
        self.asset_path: str = data['assetPath']
        self._content: Dict[Any, Any] = data['content']

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<Contract display_name={self.display_name!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Union[ContractU, Contract]) and self.uuid == other.uuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def id(self) -> str:
        """:class: `str` Returns the contract id."""
        return self.uuid

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the contract's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the contract's name."""
        return self.name_localizations.american_english

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the contract's icon."""
        return Asset._from_url(self._client, self._display_icon)

    def ship_it(self) -> bool:
        """:class: `bool` Returns whether the contract is ship it."""
        return self._ship_it

    @property
    def content(self) -> Content:
        """:class: `Content` Returns the contract's content."""
        return Content(client=self._client, data=self._content)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the contract with the given uuid."""
        data = client._assets.get_contract(uuid)
        return cls(client=client, data=data) if data else None


class ContractU(Contract):
    def __init__(self, client: Client, data: Mapping[str, Any], contract: ContractUPayload) -> None:
        super().__init__(client=client, data=data)
        self.total_progression_earned: int = contract['ContractProgression']['TotalProgressionEarned']
        self.highest_rewarded_level: int = contract['ContractProgression']['HighestRewardedLevel'][
            self.free_reward_schedule_uuid
        ]
        self.progression_level_reached: int = contract['ProgressionLevelReached']
        self.progression_towards_next_level: int = contract['ProgressionTowardsNextLevel']
        self.reward_per_chapter: int = min(len(chapter.rewards) for chapter in self.content.chapters)
        self.total_chapters: int = len(self.content.chapters)
        self.maximum_tier: int = sum(len(chapter.rewards) for chapter in self.content.chapters)

        # TODO: new algorithm {'chapter': len(rewards), 'chapter': len(rewards), ...} for accuracy
        self.chapter: int = self.progression_level_reached // self.reward_per_chapter
        self.chapter_reward_index: int = self.progression_level_reached % self.reward_per_chapter

    def __repr__(self) -> str:
        return f'<ContractU display_name={self.display_name!r}>'

    @property
    def xp(self) -> int:
        """:class: `int` Returns the contract's xp."""
        return self.progression_towards_next_level

    @property
    def current_tier(self) -> int:
        """:class: `int` Returns the contract's current tier."""
        return self.progression_level_reached

    @current_tier.setter
    def current_tier(self, value: int) -> None:
        self.progression_level_reached = value

    @property
    def current_tier_needed_xp(self) -> int:
        """:class: `int` Returns the contract's current tier needed xp."""
        return utils.calculate_level_xp(self.current_tier + 1)

    @property
    def next_tier_remaining_xp(self) -> int:
        """:class: `int` Returns the contract's next tier remaining xp."""
        return self.current_tier_needed_xp - self.xp

    @property
    def next_tier_reward(self) -> Optional[Reward]:
        """:class: `Optional[Reward]` Returns the contract's next tier reward."""

        if self.current_tier >= self.maximum_tier:
            return None

        try:
            chapter = self.content.chapters[self.chapter]
            return chapter.rewards[self.chapter_reward_index]
        except IndexError:
            return None

    @property
    def latest_tier_reward(self) -> Optional[Reward]:
        """:class: `Optional[Reward]` Returns the contract's latest tier reward."""

        try:
            chapter = self.content.chapters[self.chapter - (1 if self.chapter_reward_index == 0 else 0)]
            return chapter.rewards[self.chapter_reward_index - 1]
        except IndexError:
            return None

    @property
    def my_rewards(self) -> Iterator[Reward]:
        """:class: `Iterator[Reward]` Returns the contract's rewards."""

        if self.maximum_tier <= self.current_tier == self.highest_rewarded_level:
            for chapter in self.content.chapters:
                yield from chapter.rewards
        else:
            for i in range(0, len(self.content.chapters)):
                chapter = self.content.chapters[i]
                if i <= self.chapter:
                    if i == self.chapter:
                        yield from chapter.rewards[: self.chapter_reward_index]
                    else:
                        yield from chapter.rewards

    def get_next_reward(self) -> Optional[Union[SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]:
        """:class: `Optional[Union[SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]` Returns the next reward."""
        reward = self.next_tier_reward
        if reward:
            return reward.get_reward()
        else:
            return None

    @classmethod
    def _from_contract(cls, client: Client, contract: ContractUPayload) -> Self:
        data = client._assets.get_contract(contract['ContractDefinitionID'])
        return cls(client=client, data=data, contract=contract)


class ProcessedMatch:
    def __init__(self, data: ProcessedMatchPayload) -> None:
        self.id: str = data.get('ID', '')
        self._start_time: Union[datetime.datetime, str] = data.get('StartTime')
        self.xp_grants: Optional[Any] = data.get('XPGrants')
        self.reward_grants: Optional[Any] = data.get('RewardGrants')
        self.mission_deltas: Optional[Any] = data.get('MissionDeltas')
        self.contract_deltas: Optional[Any] = data.get('ContractDeltas')
        self._could_progress_missions: bool = data.get('CouldProgressMissions', False)

    def __repr__(self) -> str:
        return f'<ProcessedMatch id={self.id!r}>'

    def __bool__(self) -> bool:
        return self._could_progress_missions

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProcessedMatch) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def start_time(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the match's start time."""
        return utils.parse_iso_datetime(self._start_time)

    def could_progress_missions(self) -> bool:
        """:class: `bool` Returns whether the match could progress missions."""
        return self._could_progress_missions


class Contracts(BaseModel):
    def __init__(self, client: Client, data: ContractsPayload) -> None:
        super().__init__(client=client, data=data)
        self._update(data)

    def __repr__(self) -> str:
        return f'<Contracts version={self.version!r} subject={self.subject!r}>'

    def _update(self, data: ContractsPayload) -> None:
        self.version: int = data['Version']
        self.subject: str = data['Subject']
        self.contracts: List[ContractU] = [
            ContractU._from_contract(self._client, contract) for contract in data['Contracts']
        ]
        self.processed_matches: List[ProcessedMatch] = [ProcessedMatch(match) for match in data['ProcessedMatches']]
        self.active_special_contract_id: Optional[str] = data.get('ActiveSpecialContract')
        self.missions: List[MissionU] = [MissionU._from_mission(self._client, mission) for mission in data['Missions']]
        self.mission_metadata: Optional[MissionMeta] = (
            MissionMeta(data['MissionMetadata']) if data.get('MissionMetadata') else None
        )

    def special_contract(self) -> Optional[ContractU]:
        """:class: `ContractA` Returns the active special contract."""
        for contract in self.contracts:
            if contract.uuid == self.active_special_contract_id:
                return contract
        return None

    def get_latest_contract(self, relation_type: Optional[Union[RelationType, str]] = None) -> Optional[ContractU]:
        """:class: `ContractA` Returns the latest contract."""
        if relation_type is not None:
            relation_type = RelationType(relation_type) if isinstance(relation_type, str) else relation_type
            contract_list = [contract for contract in self.contracts if contract.content.relation_type == relation_type]
            return contract_list[len(contract_list) - 1] if contract_list else None
        return self.contracts[len(self.contracts) - 1] if len(self.contracts) > 0 else None

    async def activate_contract(self, contract: Union[Contract, ContractU, str]) -> Optional[Union[Contract, ContractU]]:
        """Activates the given contract."""

        if isinstance(contract, str):
            try_contract = Contract._from_uuid(self._client, contract)
            if not try_contract:
                raise InvalidContractType(f'No contract found with uuid {contract!r}')
            contract = try_contract

        if isinstance(contract, Union[Contract, ContractU]):

            if not isinstance(contract, ContractU):
                for c in self.contracts:
                    if c == contract:
                        contract = c

            if contract.content.relation_type != RelationType.agent:
                raise InvalidRelationType(f'Contract {contract.display_name!r} is not an agent contract')

            if contract == self.special_contract():
                return contract

            if contract.progression_level_reached == 10:
                _log.warning(f'Contract {contract.display_name!r} is already at max level')
                return contract
        else:
            raise TypeError(f'Expected ContractA, ContractU, or str, got {type(contract)}')

        # update the active special contract
        data = await self._client.http.contracts_activate(contract.uuid)
        self._update(data)
        return self.special_contract()

    def get_all_seasonal_contracts(self) -> List[ContractU]:
        """:class: `List[ContractU]` Returns all seasonal contracts."""
        return [contract for contract in self.contracts if contract.content.relation_type == RelationType.season]

    def get_all_agent_contracts(self) -> List[ContractU]:
        """:class: `List[ContractU]` Returns all agent contracts."""
        return [contract for contract in self.contracts if contract.content.relation_type == RelationType.agent]

    def get_all_event_contracts(self) -> List[ContractU]:
        """:class: `List[ContractU]` Returns all event contracts."""
        return [contract for contract in self.contracts if contract.content.relation_type == RelationType.event]

    @property
    def daily_mission(self) -> Iterator[MissionU]:
        """:class: `MissionU` Returns the daily mission."""
        for mission in self.missions:
            if mission.type == MissionType.daily:
                yield mission

    @property
    def weekly_mission(self) -> Iterator[MissionU]:
        """:class: `MissionU` Returns the weekly mission."""
        for mission in self.missions:
            if mission.type == MissionType.weekly:
                yield mission

    @property
    def tutorial_mission(self) -> Iterator[MissionU]:
        """:class: `MissionU` Returns the tutorial mission."""
        for mission in self.missions:
            if mission.type == MissionType.tutorial:
                yield mission

    @property
    def npe_mission(self) -> Iterator[MissionU]:
        """:class: `MissionU` Returns the npe mission."""
        for mission in self.missions:
            if mission.type == MissionType.npe:
                yield mission


class Content:
    def __init__(self, client: Client, data: Dict[str, Any]) -> None:
        self._client: Client = client
        self.relation_type: RelationType = try_enum(RelationType, data['relationType'])
        self.relation_uuid: Optional[str] = data.get('relationUuid')
        self._chapters: Optional[List[Any]] = data.get('chapters')
        self.premium_reward_schedule_uuid: Optional[str] = data.get('premiumRewardScheduleUuid')
        self.premium_vp_cost: int = data.get('premiumVPCost')

    def __repr__(self) -> str:
        return f'<Content relation={self.relation!r}>'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Content)
            and self.relation_type == other.relation_type
            and self.relation_uuid == other.relation_uuid
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def chapters(self) -> List[Chapter]:
        """:class: `List[Chapter]` Returns the chapters."""
        chapters = []
        if self._chapters is not None:
            for index, chapter in enumerate(self._chapters):
                chapters.append(Chapter(self._client, data=chapter, index=index))
        return chapters

    @property
    def relation(self) -> Union[Agent, Season, Event]:
        """:class: `Any` Returns the relation."""
        if self.relation_type == RelationType.agent:
            return self._client.get_agent(uuid=self.relation_uuid)
        elif self.relation_type == RelationType.season:
            return self._client.get_season(uuid=self.relation_uuid)
        elif self.relation_type == RelationType.event:
            return self._client.get_event(uuid=self.relation_uuid)
        else:
            _log.warning(f'Unknown relation type {self.relation_type!r} with uuid {self.relation_uuid!r}')


class Chapter:
    def __init__(self, client: Client, data: Dict[str, Any], index: int) -> None:
        self._client: Client = client
        self.index: int = index
        self._is_epilogue: bool = data.get('isEpilogue', False)
        self.levels: List[Level] = [Level(client=client, data=level, chapter_index=index) for level in data['levels']]
        self.free_rewards: List[Reward] = (
            [Reward(client=client, data=reward, is_free=True, index=index) for reward in data['freeRewards']]
            if data.get('freeRewards') is not None
            else []
        )

    def __repr__(self) -> str:
        return f'<Chapter is_epilogue={self.is_epilogue()!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Chapter) and self.index == other.index

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        return isinstance(other, Chapter) and self.index < other.index

    def __le__(self, other: object) -> bool:
        return isinstance(other, Chapter) and self.index <= other.index

    def __gt__(self, other: object) -> bool:
        return isinstance(other, Chapter) and self.index > other.index

    def __ge__(self, other: object) -> bool:
        return isinstance(other, Chapter) and self.index >= other.index

    @property
    def rewards(self) -> List[Reward]:
        """:class: `List[Reward]` Returns the rewards."""
        return [level.reward for level in self.levels]

    def is_epilogue(self) -> bool:
        return self._is_epilogue


class Level:
    def __init__(self, client: Client, data: Dict[str, Any], chapter_index: int = 0) -> None:
        self.reward: Reward = Reward(client=client, data=data['reward'], index=chapter_index)
        self.xp: int = data.get('xp', 0)
        self.vp_cost: int = data.get('vpCost', 0)
        self.is_purchasable_with_vp: bool = data.get('isPurchasableWithVP', False)

    def __repr__(self) -> str:
        return f'<Level reward={self.reward!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Level) and self.reward == other.reward

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Reward:
    def __init__(self, client: Client, data: Dict[str, Any], is_free: bool = False, index: int = 0) -> None:
        self._client: Client = client
        self.type: str = data.get('type')
        self.uuid: str = data.get('uuid')
        self.amount: int = data.get('amount', 0)
        self._is_highlighted: bool = data.get('isHighlighted', False)
        self._is_free: bool = is_free
        self.chapter_index: int = index

    def __repr__(self) -> str:
        return f'<Reward reward={self._reward!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Reward) and self.uuid == other.uuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def is_highlighted(self) -> bool:
        """:class: `bool` Returns whether the reward is highlighted."""
        return self._is_highlighted

    def is_free(self) -> bool:
        """:class: `bool` Returns whether the reward is free."""
        return self._is_free

    # special case for the free rewards

    @property
    def _reward(self) -> Optional[Union[SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]:
        if self.type == str(RewardType.skin_level):
            return self._client.get_skin_level(uuid=self.uuid)
        elif self.type == str(RewardType.buddy_level):
            return self._client.get_buddy_level(uuid=self.uuid)
        elif self.type == str(RewardType.player_card):
            return self._client.get_player_card(uuid=self.uuid)
        elif self.type == str(RewardType.player_title):
            return self._client.get_player_title(uuid=self.uuid)
        elif self.type == str(RewardType.spray):
            return self._client.get_spray(uuid=self.uuid)
        elif self.type == str(RewardType.currency):
            return self._client.get_currency(uuid=self.uuid)
        else:
            _log.warning(f'Unknown contract reward type {self.type!r} with uuid {self.uuid!r}')
            return None

    def get_reward(self) -> Optional[Union[SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]:
        """:class: `Optional[Union[SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]` Returns the reward."""
        return self._reward
