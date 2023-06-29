from __future__ import annotations

# import datetime
# import logging
import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from valorantx.valorant_api.models.contracts import (
    Chapter as Chapter,
    Content as ContentValorantAPI,
    Contract as ContractValorantAPI,
    Level as Level,
    Reward as RewardValorantAPI_,
)

from .. import utils
from ..enums import RelationType
from .missions import Mission, MissionMetadata

# from ..asset import Asset
# from ..enums import ContractRewardType as RewardType, Locale, MissionType, RelationType, try_enum
# from ..errors import InvalidContractType, InvalidRelationType
# from ..localization import Localization
# from .mission import MissionMeta, MissionU
# from .abc import Item

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.contracts import Contract as ContractValorantAPIPayload
    from valorantx.valorant_api_cache import CacheState

    from ..client import Client
    from ..types.contracts import (
        Contract as ContractPayload,
        ContractProgression as ContractProgressionPayload,
        Contracts as ContractsPayload,
        ProcessedMatch as ProcessedMatchPayload,
        RecruitmentProgressUpdate as RecruitmentProgressUpdatePayload,
        Reward as RewardPayload,
    )
    from .agents import Agent
    from .buddies import BuddyLevel
    from .currencies import Currency
    from .player_cards import PlayerCard
    from .player_titles import PlayerTitle
    from .sprays import Spray
    from .weapons import SkinLevel

    # from .event import Event
    # from .season import Season
    # Item = Union[Agent, SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]


# _log = logging.getLogger(__name__)
# fmt: off
__all__ = (
    'Chapter',
    'Content',
    'Contract',
    'Contracts',
    'Level',
    'ProcessedMatch',
    'Progression',
    'Reward',
    'RewardValorantAPI',
    'RecruitmentProgressUpdate'
)
# fmt: on


class RewardValorantAPI(RewardValorantAPI_):
    if TYPE_CHECKING:

        def get_item(self) -> Optional[Union[Agent, SkinLevel, BuddyLevel, Currency, PlayerCard, PlayerTitle, Spray]]:
            ...


class Content(ContentValorantAPI):
    if TYPE_CHECKING:

        def get_all_rewards(self) -> List[RewardValorantAPI]:
            ...


class Reward:
    def __init__(self, uuid: str, data: RewardPayload) -> None:
        self.uuid: str = uuid
        self.amount: int = data['Amount']
        self.version: int = data['Version']


class Progression:
    def __init__(
        self,
        contract: Contract,
        data: ContractProgressionPayload,
    ) -> None:
        self.earned: int = data['TotalProgressionEarned']
        self.earned_version: int = data['TotalProgressionEarnedVersion']
        self.reward: Reward = Reward(
            contract.free_reward_schedule_uuid, data['HighestRewardedLevel'][contract.free_reward_schedule_uuid]
        )


class Contract(ContractValorantAPI):
    def __init__(self, state: CacheState, data: ContractValorantAPIPayload, data_contract: ContractPayload) -> None:
        super().__init__(state=state, data=data)
        self.definition_id: str = data_contract['ContractDefinitionID']
        self.progression_level_reached: int = data_contract['ProgressionLevelReached']
        self.progression_towards_next_level: int = data_contract['ProgressionTowardsNextLevel']
        self.progression: Progression = Progression(contract=self, data=data_contract['ContractProgression'])
        self._content: Content = Content(self._state, data['content'])
        # self.maximum_levels: int = sum(len([level.reward for level in chapter.levels]) for chapter in self.content.chapters)
        # self.total_progression_earned: int = contract['ContractProgression']['TotalProgressionEarned']
        # self.highest_rewarded_level: int = contract['ContractProgression']['HighestRewardedLevel'][
        #     self.free_reward_schedule_uuid
        # ]
        # self.progression_level_reached: int = contract.get('ProgressionLevelReached', 0)
        # self.progression_towards_next_level: int = contract['ProgressionTowardsNextLevel']
        # self.reward_per_chapter: int = min(len(chapter._rewards) for chapter in self.content._chapters)
        # self.total_chapters: int = len(self.content._chapters)
        # self.maximum_tier: int = sum(len(chapter._rewards) for chapter in self.content._chapters)
        # TODO: new algorithm {'chapter': len(rewards), 'chapter': len(rewards), ...} for accuracy
        # self.chapter: int = self.progression_level_reached // self.reward_per_chapter
        # self.chapter_reward_index: int = self.progression_level_reached % self.reward_per_chapter

    def __repr__(self) -> str:
        return f'<Contract display_name={self.display_name!r}>'

    @property
    def current_level(self) -> int:
        """:class: `int` alias for :attr:`progression_level_reached`."""
        return self.progression_level_reached

    @property
    def current_tier_needed_xp(self) -> int:
        """:class: `int` Returns the contract's current tier needed xp."""
        return utils.calculate_level_xp(self.progression_level_reached + 1)

    @property
    def content(self) -> Content:
        """:class: `Content` Returns the contract's content."""
        return self._content

    # @property
    # def next_level_reward(self) -> Optional[ContractReward]:
    #     """:class: `Optional[Reward]` Returns the contract's next tier reward."""

    #     if self.progression_level_reached >= self.maximum_tier:
    #         return None

    #     try:
    #         chapter = self.content._chapters[self.chapter]
    #         return chapter._rewards[self.chapter_reward_index]
    #     except IndexError:
    #         return None

    #     @property
    #     def xp(self) -> int:
    #         """:class: `int` Returns the contract's xp."""
    #         return self.progression_towards_next_level

    #     @current_tier.setter
    #     def current_tier(self, value: int) -> None:
    #         self.progression_level_reached = value

    #     @property
    #     def current_tier_needed_xp(self) -> int:
    #         """:class: `int` Returns the contract's current tier needed xp."""
    #         return utils.calculate_level_xp(self.current_tier + 1)

    #     @property
    #     def next_tier_remaining_xp(self) -> int:
    #         """:class: `int` Returns the contract's next tier remaining xp."""
    #         return self.current_tier_needed_xp - self.xp

    #     @property
    #     def latest_tier_reward(self) -> Optional[Reward]:
    #         """:class: `Optional[Reward]` Returns the contract's latest tier reward."""

    #         try:
    #             chapter = self.content._chapters[self.chapter - (1 if self.chapter_reward_index == 0 else 0)]
    #             return chapter._rewards[self.chapter_reward_index - 1]
    #         except IndexError:
    #             return None

    #     @property
    #     def my_rewards(self) -> Iterator[Reward]:
    #         """:class: `Iterator[Reward]` Returns the contract's rewards."""

    #         if self.maximum_tier <= self.current_tier == self.highest_rewarded_level:
    #             for chapter in self.content._chapters:
    #                 yield from chapter._rewards
    #         else:
    #             for i in range(0, len(self.content._chapters)):
    #                 chapter = self.content._chapters[i]
    #                 if i <= self.chapter:
    #                     if i == self.chapter:
    #                         yield from chapter._rewards[: self.chapter_reward_index]
    #                     else:
    #                         yield from chapter._rewards

    #     def get_next_reward(self) -> Optional[Union[Agent, SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]:
    #         """:class: `Optional[Union[SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]` Returns the next reward."""
    #         reward = self.next_tier_reward
    #         return reward.get_item() if reward is not None else None

    #     def get_latest_reward(self) -> Optional[Union[Agent, SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]:
    #         """:class: `Optional[Union[SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]` Returns the latest reward."""
    #         reward = self.latest_tier_reward
    #         return reward.get_item() if reward is not None else None

    @classmethod
    def from_contract(cls, state: CacheState, data: ContractPayload) -> Self:
        contract = state.get_contract(data['ContractDefinitionID'])
        # TODO: fix this
        if contract is None:
            raise ValueError(f'Contract with uuid {data["ContractDefinitionID"]!r} not found.')
        return cls(state=state, data=contract._data, data_contract=data)


class RecruitmentProgressUpdate:
    def __init__(self, client: Client, data: RecruitmentProgressUpdatePayload) -> None:
        self._client: Client = client
        self.group_id: str = data['GroupID']
        self.progress_before: int = data['ProgressBefore']
        self.progress_after: int = data['ProgressAfter']
        self.milestone_threshold: int = data['MilestoneThreshold']

    def __repr__(self) -> str:
        return f'<RecruitmentProgressUpdate group={self.group!r}>'

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, RecruitmentProgressUpdate)
            and self.group_id == other.group_id
            and self.progress_before == other.progress_before
            and self.progress_after == other.progress_after
            and self.milestone_threshold == other.milestone_threshold
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.group_id, self.progress_before, self.progress_after, self.milestone_threshold))

    @property
    def group(self) -> Optional[Agent]:
        return self._client.valorant_api.get_agent(self.group_id)


class ProcessedMatch:
    def __init__(self, client: Client, data: ProcessedMatchPayload) -> None:
        self._client: Client = client
        self.id: str = data['ID']
        self._start_time: int = data['StartTime']
        self.xp_grants: Optional[Any] = data['XPGrants']
        self.reward_grants: Optional[Any] = data['RewardGrants']
        self.mission_deltas: Optional[Any] = data['MissionDeltas']
        self.contract_deltas: Optional[Any] = data['ContractDeltas']
        self.recruitment_progress_update: Optional[RecruitmentProgressUpdate] = None
        if 'RecruitmentProgressUpdate' in data:
            self.recruitment_progress_update = RecruitmentProgressUpdate(client, data['RecruitmentProgressUpdate'])
        self.could_progress_missions: bool = data['CouldProgressMissions']

    def __repr__(self) -> str:
        return f'<ProcessedMatch id={self.id!r}>'

    def __bool__(self) -> bool:
        return self.could_progress_missions

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProcessedMatch) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def start_time(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the match's start time."""
        return utils.parse_iso_datetime(str(self._start_time))


class Contracts:
    subject: str
    version: int
    processed_matches: List[ProcessedMatch]
    missions: List[Mission]
    mission_metadata: Optional[MissionMetadata]

    def __init__(self, client: Client, data: ContractsPayload) -> None:
        self._client: Client = client
        self._update(data)

    def __repr__(self) -> str:
        return f'<Contracts version={self.version!r} subject={self.subject!r}>'

    def _update(self, data: ContractsPayload) -> None:
        self.version: int = data['Version']
        self.subject: str = data['Subject']
        self._contracts: Dict[str, Contract] = {
            contract['ContractDefinitionID']: Contract.from_contract(self._client.valorant_api.cache, contract)
            for contract in data['Contracts']
        }
        self.processed_matches: List[ProcessedMatch] = [
            ProcessedMatch(self._client, match) for match in data['ProcessedMatches']
        ]
        self.active_special_contract_id: Optional[str] = data['ActiveSpecialContract']  # data.get('ActiveSpecialContract')
        self.missions: List[Mission] = []
        self.mission_metadata: Optional[MissionMetadata] = None
        if data['MissionMetadata'] is not None:
            self.mission_metadata = MissionMetadata(data['MissionMetadata'])
        for m in data['Missions']:
            mission = Mission.from_contract(self._client.valorant_api.cache, m)
            if mission is not None:
                self.missions.append(mission)

    # helper methods
    # TODO: add helper methods

    @property
    def contracts(self) -> List[Contract]:
        """:class: `List[Contract]` Returns all contracts."""
        return list(self._contracts.values())

    def get_contract(self, uuid: str) -> Optional[Contract]:
        """:class: `Optional[Contract]` Returns a contract by uuid."""
        return self._contracts.get(uuid)

    @property
    def special_contract(self) -> Optional[Contract]:
        """:class: `ContractA` Returns the active special contract."""
        for contract in self.contracts:
            if contract.uuid == self.active_special_contract_id:
                return contract
        return None

    def get_all_seasonal_contracts(self) -> List[Contract]:
        """:class: `List[ContractU]` Returns all seasonal contracts."""
        return [contract for contract in self.contracts if contract.content.relation_type is RelationType.season]

    def get_all_agent_contracts(self) -> List[Contract]:
        """:class: `List[ContractU]` Returns all agent contracts."""
        return [contract for contract in self.contracts if contract.content.relation_type is RelationType.agent]

    def get_all_event_contracts(self) -> List[Contract]:
        """:class: `List[ContractU]` Returns all event contracts."""
        return [contract for contract in self.contracts if contract.content.relation_type is RelationType.event]

    # helpers

    def get_latest_contract(self, relation_type: Optional[RelationType] = None) -> Contract:
        """:class: `ContractA` Returns the latest contract."""
        if relation_type is not None:
            contract_list = [contract for contract in self.contracts if contract.content.relation_type is relation_type]
            return contract_list[len(contract_list) - 1]
        return self.contracts[len(self.contracts) - 1]

    # def get_contract_by_type(self, relation_type: Union[RelationType, str]) -> List[Contract]:
    #     """:class: `List[ContractU]` Returns all seasonal contracts."""
    # TODO: in latte bot
    #     ...

    # @property
    # def daily_mission(self) -> List[Mission]:
    #     """:class: `MissionU` Returns the daily mission."""
    #     return [mission for mission in self.missions if mission.type == MissionType.daily]
    #     # for mission in self.missions:
    #     #     if mission.type == MissionType.daily:
    #     #         yield mission

    # @property
    # def weekly_mission(self) -> List[Mission]:
    #     """:class: `MissionU` Returns the weekly mission."""
    #     return [mission for mission in self.missions if mission.type == MissionType.weekly]

    # @property
    # def tutorial_mission(self) -> List[Mission]:
    #     """:class: `MissionU` Returns the tutorial mission."""

    # @property
    # def npe_mission(self) -> List[Mission]:
    #     """:class: `MissionU` Returns the npe mission."""
    #     return [mission for mission in self.missions if mission.type == MissionType.npe]


#     def get_latest_contract(self, relation_type: Optional[Union[RelationType, str]] = None) -> Optional[ContractU]:
#         """:class: `ContractA` Returns the latest contract."""
#         if relation_type is not None:
#             relation_type = RelationType(relation_type) if isinstance(relation_type, str) else relation_type
#             contract_list = [contract for contract in self.contracts if contract.content.relation_type == relation_type]
#             return contract_list[len(contract_list) - 1] if contract_list else None
#         return self.contracts[len(self.contracts) - 1] if len(self.contracts) > 0 else None

#     async def activate_contract(self, contract: Union[Contract, ContractU, str]) -> Optional[Union[Contract, ContractU]]:
#         """Activates the given contract."""

#         if isinstance(contract, str):
#             try_contract = Contract._from_uuid(self._client, contract)
#             if not try_contract:
#                 raise InvalidContractType(f'No contract found with uuid {contract!r}')
#             contract = try_contract

#         if not isinstance(contract, (Contract, ContractU)):
#             raise TypeError(f'Expected ContractA, ContractU, or str, got {type(contract)}')

#         if not isinstance(contract, ContractU):
#             for c in self.contracts:
#                 if c == contract:
#                     contract = c

#         if contract.content.relation_type != RelationType.agent:
#             raise InvalidRelationType(f'Contract {contract.display_name!r} is not an agent contract')

#         if contract == self.special_contract():
#             return contract

#         if isinstance(contract, ContractU):
#             if contract.current_tier == 10:
#                 _log.warning(f'Contract {contract.display_name!r} is already at max level')
#                 return contract

#         # update the active special contract
#         data = await self._client.http.contracts_activate(contract.uuid)
#         self._update(data)
#         return self.special_contract()

#     @property
#     def daily_mission(self) -> Iterator[MissionU]:
#         """:class: `MissionU` Returns the daily mission."""
#         for mission in self.missions:
#             if mission.type == MissionType.daily:
#                 yield mission

#     @property
#     def weekly_mission(self) -> Iterator[MissionU]:
#         """:class: `MissionU` Returns the weekly mission."""
#         for mission in self.missions:
#             if mission.type == MissionType.weekly:
#                 yield mission

#     @property
#     def tutorial_mission(self) -> Iterator[MissionU]:
#         """:class: `MissionU` Returns the tutorial mission."""
#         for mission in self.missions:
#             if mission.type == MissionType.tutorial:
#                 yield mission

#     @property
#     def npe_mission(self) -> Iterator[MissionU]:
#         """:class: `MissionU` Returns the npe mission."""
#         for mission in self.missions:
#             if mission.type == MissionType.npe:
#                 yield mission


# class Content:
#     def __init__(self, client: Client, data: Dict[str, Any]) -> None:
#         self._client: Client = client
#         self.relation_type: RelationType = try_enum(RelationType, data['relationType'])
#         self.relation_uuid: Optional[str] = data.get('relationUuid')
#         self.premium_reward_schedule_uuid: Optional[str] = data.get('premiumRewardScheduleUuid')
#         self.premium_vp_cost: int = data.get('premiumVPCost', 0)
#         self._chapters: List[Chapter] = []
#         self.relation: Optional[Union[Agent, Season, Event]] = None
#         if self.relation_type == RelationType.agent:
#             self.relation = client.get_agent(uuid=self.relation_uuid)
#         elif self.relation_type == RelationType.season:
#             self.relation = client.get_season(uuid=self.relation_uuid)
#         elif self.relation_type == RelationType.event:
#             self.relation = client.get_event(uuid=self.relation_uuid)
#         if chapters := data.get('chapters'):
#             for index, chapter in enumerate(chapters):
#                 self._chapters.append(Chapter(client, data=chapter, index=index))

#     def __repr__(self) -> str:
#         return f'<Content relation={self.relation!r}>'

#     def __eq__(self, other: object) -> bool:
#         return (
#             isinstance(other, Content)
#             and self.relation_type == other.relation_type
#             and self.relation_uuid == other.relation_uuid
#         )

#     def __ne__(self, other: object) -> bool:
#         return not self.__eq__(other)

#     def get_chapters(self) -> List[Chapter]:
#         """:class: `List[Chapter]` Returns the chapters."""
#         return self._chapters

#     def get_all_rewards(self) -> List[Reward]:
#         """:class: `List[Reward]` Returns all rewards."""
#         rewards = []
#         for chapter in self.get_chapters():
#             rewards.extend(chapter._rewards)
#         return rewards


# class Chapter:
#     def __init__(self, client: Client, data: Dict[str, Any], index: int) -> None:
#         self._client: Client = client
#         self.index: int = index
#         self._is_epilogue: bool = data.get('isEpilogue', False)
#         self.levels: List[Level] = [Level(client=client, data=level, chapter_index=index) for level in data['levels']]
#         self._rewards: List[Reward] = [level.reward for level in self.levels]
#         self.free_rewards: List[Reward] = (
#             [Reward(client=client, data=reward, is_free=True, index=index) for reward in data['freeRewards']]
#             if data.get('freeRewards') is not None
#             else []
#         )

#     def __repr__(self) -> str:
#         return f'<Chapter is_epilogue={self.is_epilogue()!r}>'

#     def __eq__(self, other: object) -> bool:
#         return isinstance(other, Chapter) and self.index == other.index

#     def __ne__(self, other: object) -> bool:
#         return not self.__eq__(other)

#     def __lt__(self, other: object) -> bool:
#         return isinstance(other, Chapter) and self.index < other.index

#     def __le__(self, other: object) -> bool:
#         return isinstance(other, Chapter) and self.index <= other.index

#     def __gt__(self, other: object) -> bool:
#         return isinstance(other, Chapter) and self.index > other.index

#     def __ge__(self, other: object) -> bool:
#         return isinstance(other, Chapter) and self.index >= other.index

#     def is_epilogue(self) -> bool:
#         return self._is_epilogue

#     def get_rewards(self) -> List[Reward]:
#         """:class: `List[Reward]` Returns the rewards."""
#         return self._rewards


# class Level:
#     def __init__(self, client: Client, data: Dict[str, Any], chapter_index: int = 0) -> None:
#         self.reward: Reward = Reward(client=client, data=data['reward'], index=chapter_index)
#         self.xp: int = data.get('xp', 0)
#         self.vp_cost: int = data.get('vpCost', 0)
#         self.is_purchasable_with_vp: bool = data.get('isPurchasableWithVP', False)

#     def __repr__(self) -> str:
#         return f'<Level reward={self.reward!r}>'

#     def __eq__(self, other: object) -> bool:
#         return isinstance(other, Level) and self.reward == other.reward

#     def __ne__(self, other: object) -> bool:
#         return not self.__eq__(other)


# class Reward:
#     def __init__(self, client: Client, data: Dict[str, Any], is_free: bool = False, index: int = 0) -> None:
#         self._client: Client = client
#         self.type: RewardType = try_enum(RewardType, data['type'])
#         self.uuid: str = data['uuid']
#         self.amount: int = data.get('amount', 0)
#         self._is_highlighted: bool = data.get('isHighlighted', False)
#         self._is_free: bool = is_free
#         self.chapter_index: int = index
#         self._reward: Optional[Item] = None
#         if self.type == RewardType.skin_level:
#             self._reward = self._client.get_skin_level(uuid=self.uuid)
#         elif self.type == RewardType.buddy_level:
#             self._reward = self._client.get_buddy_level(uuid=self.uuid)
#         elif self.type == RewardType.player_card:
#             self._reward = self._client.get_player_card(uuid=self.uuid)
#         elif self.type == RewardType.player_title:
#             self._reward = self._client.get_player_title(uuid=self.uuid)
#         elif self.type == RewardType.spray:
#             self._reward = self._client.get_spray(uuid=self.uuid, level=False)
#         elif self.type == RewardType.currency:
#             self._reward = self._client.get_currency(uuid=self.uuid)
#         elif self.type == RewardType.agent:
#             self._reward = self._client.get_agent(uuid=self.uuid)
#         else:
#             _log.warning(f'Unknown contract reward type {self.type!r} with uuid {self.uuid!r}')

#     def __repr__(self) -> str:
#         return f'<Reward reward={self._reward!r}>'

#     def __eq__(self, other: object) -> bool:
#         return isinstance(other, Reward) and self.uuid == other.uuid

#     def __ne__(self, other: object) -> bool:
#         return not self.__eq__(other)

#     def get_item(self) -> Optional[Item]:
#         """:class: `Optional[Union[SkinLevel, BuddyLevel, PlayerCard, PlayerTitle, Spray, Currency]]` Returns the reward."""
#         return self._reward

#     def is_highlighted(self) -> bool:
#         """:class: `bool` Returns whether the reward is highlighted."""
#         return self._is_highlighted

#     def is_free(self) -> bool:
#         """:class: `bool` Returns whether the reward is free."""
#         return self._is_free
