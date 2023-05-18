from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from valorantx.valorant_api.models.sprays import Spray as SprayValorantAPI, SprayLevel as SprayLevelValorantAPI

from .abc import BundleItemOffer, Item

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.sprays import (
        Spray as SprayPayloadValorantAPI,
        SprayLevel as SprayLevelPayloadValorantAPI,
    )

    from ..types.store import BundleItemOffer as BundleItemOfferPayload
    from ..valorant_api_cache import CacheState


class Spray(SprayValorantAPI, Item):
    def __init__(self, *, state: CacheState, data: SprayPayloadValorantAPI) -> None:
        super().__init__(state=state, data=data)
        Item.__init__(self)
        self.levels: List[SprayLevel] = [SprayLevel(state=state, data=level, parent=self) for level in data['levels']]


class SprayLevel(SprayLevelValorantAPI['Spray']):
    def __init__(self, *, state: CacheState, data: SprayLevelPayloadValorantAPI, parent: Spray) -> None:
        super().__init__(state=state, data=data, parent=parent)

    # helpers

    @property
    def cost(self) -> int:
        return self.parent.cost

    @property
    def price(self) -> int:
        return self.cost


class SprayBundle(Spray, BundleItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: SprayPayloadValorantAPI,
        data_bundle: BundleItemOfferPayload,
    ) -> None:
        Spray.__init__(self, state=state, data=data)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<SprayBundle display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bundle: BundleItemOfferPayload) -> Optional[Self]:
        spray = state.get_spray(data_bundle['BundleItemOfferID'])
        if spray is None:
            return None
        return cls(state=state, data=spray._data, data_bundle=data_bundle)
