from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, List, Optional, Union

from valorant.models.bundles import Bundle as BundleValorantAPI

from ..enums import VALORANT_POINT_UUID, ItemTypeID, try_enum
from .abc import Item
from .buddies import BuddyLevelBundle
from .player_cards import PlayerCardBundle
from .player_titles import PlayerTitleBundle
from .sprays import SprayBundle
from .weapons import SkinLevelBundle

if TYPE_CHECKING:
    from typing_extensions import Self
    from valorant.types.bundles import Bundle as BundleValorantAPIPayload

    from ..types.store import Bundle_ as BundlePayload
    from ..valorant_api_cache import CacheState
    from .buddies import Buddy
    from .player_cards import PlayerCard
    from .player_titles import PlayerTitle
    from .sprays import Spray
    from .weapons import Skin

    BundleItem = Union[Skin, Buddy, Spray, PlayerCard, PlayerTitle]
    FeaturedBundleItem = Union[BuddyLevelBundle, PlayerCardBundle, SkinLevelBundle, SprayBundle, PlayerTitleBundle]


_log = logging.getLogger(__name__)

# fmt: off
__all__ = (
    'Bundle',
    'FeaturedBundle',
)
# fmt: on


class Bundle(BundleValorantAPI, Item):
    def __init__(self, state: CacheState, data: BundleValorantAPIPayload) -> None:
        self._data = data
        super().__init__(state=state, data=data)

    if TYPE_CHECKING:
        _items: List[BundleItem] = []

        @property
        def items(self) -> List[BundleItem]:
            return super().items  # type: ignore


class FeaturedBundle(Bundle):
    def __init__(self, state: CacheState, data: BundleValorantAPIPayload, data_bundle: BundlePayload) -> None:
        super().__init__(state=state, data=data)
        self._currency_id: str = data_bundle['CurrencyID']

        self._items: List[FeaturedBundleItem] = []
        if data_bundle['ItemOffers'] is not None:
            for item in data_bundle['ItemOffers']:
                for reward in item['Offer']['Rewards']:
                    item_type = try_enum(ItemTypeID, reward['ItemTypeID'])
                    item_offer_id = item['BundleItemOfferID']
                    if item_type == ItemTypeID.skin_level:
                        skin_level = state.get_skin_level(item_offer_id)
                        if skin_level is not None:
                            self._items.append(SkinLevelBundle.from_bundle(skin_level=skin_level, data=item))
                    elif item_type == ItemTypeID.spray:
                        spray = state.get_spray(item_offer_id)
                        if spray is not None:
                            self._items.append(SprayBundle.from_bundle(spray=spray, data=item))
                    elif item_type == ItemTypeID.buddy_level:
                        buddy_level = state.get_buddy_level(item_offer_id)
                        if buddy_level is not None:
                            self._items.append(BuddyLevelBundle.from_bundle(buddy_level=buddy_level, data=item))
                    elif item_type == ItemTypeID.player_card:
                        player_card = state.get_player_card(item_offer_id)
                        if player_card is not None:
                            self._items.append(PlayerCardBundle.from_bundle(player_card=player_card, data=item))
                    elif item_type == ItemTypeID.player_title:
                        player_title = state.get_player_title(item_offer_id)
                        if player_title is not None:
                            self._items.append(PlayerTitleBundle.from_bundle(player_title=player_title, data=item))
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
    def items(self) -> List[FeaturedBundleItem]:
        """:class:`List[Union[BuddyLevelBundle, PlayerCardBundle, SkinLevelBundle, SprayBundle]]`: List of items in the bundle."""
        return self._items

    @classmethod
    def from_data(cls, state: CacheState, data: BundlePayload) -> Optional[Self]:
        bundle = state.get_bundle(data['DataAssetID'])
        if bundle is None:
            return None
        return cls(state=state, data=bundle._data, data_bundle=data)  # type: ignore
