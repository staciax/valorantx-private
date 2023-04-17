from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List

from ..enums import VALORANT_POINT_UUID

if TYPE_CHECKING:
    from ..types.store import BundleItemOffer as BundleItemOfferPayload, Offer as ItemOfferPayload, Reward as RewardPayload

# fmt: off
__all__ = (
    'Item',
    'BundleItemOffer',
)
# fmt: on


class Item:
    def __init__(self) -> None:
        self._cost = 0

    @property
    def cost(self) -> int:
        return self._cost

    @cost.setter
    def cost(self, value: int) -> None:
        self._cost = value

    @property
    def price(self) -> int:
        """:class:`int`: alias for :attr:`cost`"""
        return self.cost


class ItemOffer:
    def __init__(self, data: ItemOfferPayload) -> None:
        self._offer_id: str = data['OfferID']
        self._is_direct_purchase: bool = data['IsDirectPurchase']
        self._start_date: str = data['StartDate']
        self._cost: int = data['Cost'][VALORANT_POINT_UUID]
        self._rewards: List[RewardPayload] = data['Rewards']

    def is_direct_purchase(self) -> bool:
        return self._is_direct_purchase

    @property
    def start_date(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_date)


class BundleItemOffer:
    def __init__(self, data: BundleItemOfferPayload) -> None:
        self._bundle_item_offer_id: str = data['BundleItemOfferID']
        # avoid circular import
        from .store import Offer

        self.offer: Offer = Offer(data['Offer'], self)
        if hasattr(self.offer, 'cost'):
            self.cost = self.offer.cost
        self._discounted_cost: int = data['DiscountedCost'][VALORANT_POINT_UUID]
        self._discount_percent: float = data['DiscountPercent']

    @property
    def discounted_cost(self) -> int:
        return self._discounted_cost

    @property
    def discount_percent(self) -> float:
        return self._discount_percent
