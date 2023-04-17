from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import VALORANT_POINT_UUID

if TYPE_CHECKING:
    from ..types.store import ItemOffer as ItemOfferPayload

# fmt: off
__all__ = (
    '_Cost',
    'BundleItemOffer',
)
# fmt: on


class _Cost:
    def __init__(self) -> None:
        self._cost: int = 0

    @property
    def cost(self) -> int:
        return self._cost

    # @cost.setter
    # def cost(self, cost: int) -> None:
    #     self._cost = cost

    @property
    def price(self) -> int:
        """:class:`int`: alias for :attr:`cost`"""
        return self.cost

    # @price.setter
    # def price(self, price: int) -> None:
    #     self.cost = price


class BundleItemOffer:
    if TYPE_CHECKING:
        _cost: int

    def __init__(self, data: ItemOfferPayload) -> None:
        # avoid circular import
        self._bundle_item_offer_id: str = data['BundleItemOfferID']
        from .store import Offer

        self.offer: Offer = Offer(data['Offer'])
        self._discounted_cost: int = data['DiscountedCost'][VALORANT_POINT_UUID]
        self._discount_percent: float = data['DiscountPercent']

    @property
    def discounted_cost(self) -> int:
        return self._discounted_cost

    @property
    def discount_percent(self) -> float:
        return self._discount_percent
