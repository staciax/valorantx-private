from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, List, Union

from valorant.models.bundles import Bundle as BundleValorantAPI

from ..enums import VALORANT_POINT_UUID  # , ItemTypeID, try_enum
from .abc import Item
from .buddies import BuddyLevelBundle
from .player_cards import PlayerCardBundle
from .player_titles import PlayerTitleBundle
from .sprays import SprayBundle
from .weapons import SkinLevelBundle

if TYPE_CHECKING:
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
    _items: List[BundleItem] = []

    def __init__(self, state: CacheState, data: BundleValorantAPIPayload) -> None:
        super().__init__(state=state, data=data)

    if TYPE_CHECKING:

        @property
        def items(self) -> List[BundleItem]: ...


class FeaturedBundle:
    def __init__(self, bundle: Bundle, data: BundlePayload) -> None:
        self._bundle = bundle
        self._items: List[FeaturedBundleItem] = []
        self._currency_id: str = data['CurrencyID']
        self.total_base_item: int = 0
        if data['TotalBaseCost'] is not None:
            self.total_base_item = data['TotalBaseCost'][VALORANT_POINT_UUID]
        if data['TotalDiscountedCost'] is not None:
            self._total_discounted_cost = data['TotalDiscountedCost'][VALORANT_POINT_UUID]
        self.total_discount_percent: float = data['TotalDiscountPercent']
        self.duration_remaining_in_seconds: int = data['DurationRemainingInSeconds']
        self.wholesale_only: bool = data['WholesaleOnly']
        # if data['ItemOffers'] is not None:
        #     for item in data['ItemOffers']:
        #         for reward in item['Offer']['Rewards']:
        #             item_type = try_enum(ItemTypeID, reward['ItemTypeID'])
        #             item_offer_id = item['BundleItemOfferID']
        #             if item_type == ItemTypeID.skin_level:
        #                 skin_level = self._state.get_skin_level(item_offer_id)
        #                 if skin_level is not None:
        #                     self._items.append(SkinLevelBundle.from_bundle(skin_level=skin_level, data=item))
        #             elif item_type == ItemTypeID.spray:
        #                 spray = self._state.get_spray(item_offer_id)
        #                 if spray is not None:
        #                     self._items.append(SprayBundle.from_bundle(spray=spray, data=item))
        #             elif item_type == ItemTypeID.buddy_level:
        #                 buddy_level = self._state.get_buddy_level(item_offer_id)
        #                 if buddy_level is not None:
        #                     self._items.append(BuddyLevelBundle.from_bundle(buddy_level=buddy_level, data=item))
        #             elif item_type == ItemTypeID.player_card:
        #                 player_card = self._state.get_player_card(item_offer_id)
        #                 if player_card is not None:
        #                     self._items.append(PlayerCardBundle.from_bundle(player_card=player_card, data=item))
        #             elif item_type == ItemTypeID.player_title:
        #                 player_title = self._state.get_player_title(item_offer_id)
        #                 if player_title is not None:
        #                     self._items.append(PlayerTitleBundle.from_bundle(player_title=player_title, data=item))
        #             else:
        #                 _log.warning('Unknown item type: %s uuid: %s', item_type, reward['ItemID'])

    def __repr__(self) -> str:
        return self._bundle.__repr__()

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
