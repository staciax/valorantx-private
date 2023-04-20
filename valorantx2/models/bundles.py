from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Union

import datetime
from ..enums import VALORANT_POINT_UUID, ItemType
from ..valorant_api.models.bundles import Bundle as BundleValorantAPI
from .abc import Item
from .buddies import BuddyLevelBundle
from .player_cards import PlayerCardBundle
from .sprays import SprayBundle
from .weapons import SkinLevelBundle

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.store import Bundle_ as BundlePayload
    from ..valorant_api.types.bundles import Bundle as BundleValorantAPIPayload
    from ..valorant_api_cache import CacheState

_log = logging.getLogger(__name__)


class Bundle(BundleValorantAPI, Item):
    def __init__(self, state: CacheState, data: BundleValorantAPIPayload) -> None:
        super().__init__(state=state, data=data)


class FeaturedBundle(Bundle):
    def __init__(self, state: CacheState, data: BundleValorantAPIPayload, data_bundle: BundlePayload) -> None:
        super().__init__(state=state, data=data)
        self._currency_id: str = data_bundle['CurrencyID']

        self._items: List[Union[BuddyLevelBundle, PlayerCardBundle, SkinLevelBundle, SprayBundle]] = []
        if data_bundle['ItemOffers'] is not None:
            for item in data_bundle['ItemOffers']:
                for reward in item['Offer']['Rewards']:
                    item_type = reward['ItemTypeID']
                    if item_type == ItemType.skin_level.value:
                        skin_level = SkinLevelBundle.from_data(state=state, data_bundle=item)
                        if skin_level is not None:
                            self._items.append(skin_level)
                    elif item_type == ItemType.spray.value:
                        spray = SprayBundle.from_data(state=state, data_bundle=item)
                        if spray is not None:
                            self._items.append(spray)
                    elif item_type == ItemType.buddy_level.value:
                        buddy_level = BuddyLevelBundle.from_data(state=state, data_bundle=item)
                        if buddy_level is not None:
                            self._items.append(buddy_level)
                    elif item_type == ItemType.player_card.value:
                        player_card = PlayerCardBundle.from_data(state=state, data_bundle=item)
                        if player_card is not None:
                            self._items.append(player_card)
                    else:
                        _log.warning('Unknown item type: %s uuid: %s', item_type, reward['ItemID'])

        self.total_base_item: int = 0
        if data_bundle['TotalBaseCost'] is not None:
            self.total_base_item = self.Item = data_bundle['TotalBaseCost'][VALORANT_POINT_UUID]
        self._total_discounted_cost: int = 0
        if data_bundle['TotalDiscountedCost'] is not None:
            self._total_discounted_cost = data_bundle['TotalDiscountedCost'][VALORANT_POINT_UUID]
        self.total_discount_percent: float = data_bundle['TotalDiscountPercent']
        self.duration_remaining_in_seconds: int = data_bundle['DurationRemainingInSeconds']
        self.wholesale_only: bool = data_bundle['WholesaleOnly']

    @property
    def discounted_cost(self) -> int:
        return self._total_discounted_cost

    @property
    def cost(self) -> int:
        return self.total_base_item

    @property
    def remaining_time_utc(self) -> datetime.datetime:
        dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.duration_remaining_in_seconds)
        return dt

    @property
    def items(self) -> List[Union[BuddyLevelBundle, PlayerCardBundle, SkinLevelBundle, SprayBundle]]:
        """:class:`List[Union[BuddyLevelBundle, PlayerCardBundle, SkinLevelBundle, SprayBundle]]`: List of items in the bundle."""
        return self._items

    @classmethod
    def from_data(cls, state: CacheState, data: BundlePayload) -> Optional[Self]:
        bundle = state.get_bundle(data['DataAssetID'])
        if bundle is None:
            return None
        return cls(state=state, data=bundle._data, data_bundle=data)
