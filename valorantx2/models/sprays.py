from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ..valorant_api.models.sprays import Spray as SprayValorantAPI, SprayLevel as SprayLevelValorantAPI
from .abc import BundleItemOffer, _Cost

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.store import ItemOffer as ItemOfferPayload
    from ..valorant_api.types.sprays import Spray as SprayPayloadValorantAPI, SprayLevel as SprayLevelPayloadValorantAPI
    from ..valorant_api_cache import CacheState


class Spray(SprayValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: SprayPayloadValorantAPI) -> None:
        super().__init__(state=state, data=data)


class SprayLevel(SprayLevelValorantAPI['Spray'], _Cost):
    def __init__(self, *, state: CacheState, data: SprayLevelPayloadValorantAPI, parent: Spray) -> None:
        super().__init__(state=state, data=data, parent=parent)


class SprayBundle(Spray, BundleItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: SprayPayloadValorantAPI,
        data_bundle: ItemOfferPayload,
    ) -> None:
        Spray.__init__(self, state=state, data=data)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<SprayBundle display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bundle: ItemOfferPayload) -> Optional[Self]:
        spray = state.get_spray(data_bundle['BundleItemOfferID'])
        if spray is None:
            return None
        return cls(state=state, data=spray._data, data_bundle=data_bundle)
