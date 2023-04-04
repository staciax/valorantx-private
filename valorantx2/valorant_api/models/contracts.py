from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Union

from ..asset import Asset
from ..enums import Locale, RelationType, RewardType, try_enum
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    from ..cache import CacheState
    from ..types.contracts import (
        Chapter as ChapterPayload,
        Content as ContentPayload,
        Contract as ContractPayload,
        Level as LevelPayload,
        Reward as RewardPayload,
    )

# fmt: off
__all__ = (
    'Contract',
)
# fmt: on


class Reward(BaseModel):
    def __init__(self, state: CacheState, data: RewardPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self.type: RewardType = try_enum(RewardType, data['type'])
        self.amount: int = data['amount']
        self._is_highlighted: bool = data['isHighlighted']

    @property
    def item(self) -> ...:
        return ...

    def is_highlighted(self) -> bool:
        return self._is_highlighted


class Level:
    def __init__(self, state: CacheState, data: LevelPayload) -> None:
        self._state: CacheState = state
        self.reward: Reward = Reward(self._state, data['reward'])
        self.xp: int = data['xp']
        self.vp_cost: int = data['vpCost']
        self._is_purchasable_with_vp: bool = data['isPurchasableWithVP']

    def is_purchasable_with_vp(self) -> bool:
        return self._is_purchasable_with_vp


class Chapter:
    def __init__(self, state: CacheState, data: ChapterPayload) -> None:
        self._state: CacheState = state
        self._is_epilogue: bool = data['isEpilogue']
        self.levels: List[Level] = [Level(self._state, level) for level in data['levels']]
        self.free_rewards: Optional[List[Reward]] = None
        if data['freeRewards'] is not None:
            self.free_rewards = [Reward(self._state, reward) for reward in data['freeRewards']]

    def is_epilogue(self) -> bool:
        return self._is_epilogue


class Content:
    def __init__(self, state: CacheState, data: ContentPayload) -> None:
        self._state: CacheState = state
        self.relation_type: RelationType = try_enum(RelationType, data['relationType'])
        self._relation_uuid: str = data['relationUuid']
        self._chapters: List[Chapter] = [Chapter(self._state, chapter) for chapter in data['chapters']]
        self._premium_reward_schedule_uuid: str = data['premiumRewardScheduleUuid']
        self.premium_vp_cost: int = data['premiumVPCost']

    @property
    def chapters(self) -> List[Chapter]:
        return self._chapters

    @property
    def relation(self) -> ...:
        ...

    @property
    def premium_reward_chedule(self) -> ...:
        ...


class Contract(BaseModel):
    def __init__(self, state: CacheState, data: ContractPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self.ship_it: bool = data['shipIt']
        self._free_reward_schedule_uuid: str = data['freeRewardScheduleUuid']
        self._content: Content = Content(self._state, data['content'])
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Contract display_name={self.display_name!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Contract) and self.uuid == other.uuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def id(self) -> str:
        """:class: `str` Returns the contract id."""
        return self.uuid

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the contract's name."""
        return self._display_name_localized

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the contract's icon."""
        if self._display_icon is None:
            return None
        return Asset._from_url(self._state, self._display_icon)

    @property
    def content(self) -> Content:
        """:class: `Content` Returns the contract's content."""
        return self._content

    @property
    def free_reward_schedule(self) -> ...:
        return ...

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the contract with the given uuid."""
    #     data = client._assets.get_contract(uuid)
    #     return cls(client=client, data=data) if data else None
