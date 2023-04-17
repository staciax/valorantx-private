from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from ..valorant_api.models.weapons import (
    Skin as SkinValorantAPI,
    SkinChroma as SkinChromaValorantAPI,
    SkinLevel as SkinLevelValorantAPI,
    Weapon as WeaponValorantAPI,
)
from .abc import BundleItemOffer, Item, ItemOffer

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.store import BundleItemOffer as BundleItemOfferPayload, Offer as OfferPayload
    from ..valorant_api.types.weapons import (
        Skin as ValorantAPISkinPayload,
        SkinChroma as ValorantAPISkinChromaPayload,
        SkinLevel as ValorantAPISkinLevelPayload,
        Weapon as ValorantAPIWeaponPayload,
    )
    from ..valorant_api_cache import CacheState


class Weapon(WeaponValorantAPI, Item):
    def __init__(self, *, state: CacheState, data: ValorantAPIWeaponPayload) -> None:
        super().__init__(state=state, data=data)
        self.skins: List[Skin] = [Skin(state=state, data=skin, parent=self) for skin in data['skins']]
        Item.__init__(self)


class Skin(SkinValorantAPI['Weapon'], Item):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinPayload, parent: Weapon) -> None:
        super().__init__(state=state, data=data, parent=parent)
        self._chromas: List[SkinChroma] = [SkinChroma(state=state, data=chroma, parent=self) for chroma in data['chromas']]
        self._levels: List[SkinLevel] = [
            SkinLevel(state=state, data=level, parent=self, level_number=index) for index, level in enumerate(data['levels'])
        ]
        Item.__init__(self)

    @property
    def chromas(self) -> List[SkinChroma]:
        """:class: `list` Returns the skin's chromas."""
        return self._chromas

    @property
    def levels(self) -> List[SkinLevel]:
        """:class: `list` Returns the skin's levels."""
        return self._levels


class SkinLevel(SkinLevelValorantAPI['Skin'], Item):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinLevelPayload, parent: Skin, level_number: int) -> None:
        super().__init__(state=state, data=data, parent=parent, level_number=level_number)
        Item.__init__(self)


class SkinChroma(SkinChromaValorantAPI['Skin'], Item):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinChromaPayload, parent: Skin) -> None:
        super().__init__(state=state, data=data, parent=parent)
        Item.__init__(self)


class SkinLevelOffer(SkinLevel, ItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: ValorantAPISkinLevelPayload,
        parent: Skin,
        level_number: int,
        data_offer: OfferPayload,
    ) -> None:
        SkinLevel.__init__(self, state=state, data=data, parent=parent, level_number=level_number)
        ItemOffer.__init__(self, data=data_offer)

    def __repr__(self) -> str:
        return f'<SkinLevelOffer display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_offer: OfferPayload) -> Optional[Self]:
        skin_level = state.get_skin_level(data_offer['OfferID'])
        if skin_level is None:
            return None
        return cls(
            state=state,
            data=skin_level._data,
            parent=skin_level.parent,
            level_number=skin_level.level_number,
            data_offer=data_offer,
        )


class SkinLevelBundle(SkinLevel, BundleItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: ValorantAPISkinLevelPayload,
        parent: Skin,
        level_number: int,
        data_bundle: BundleItemOfferPayload,
    ) -> None:
        SkinLevel.__init__(self, state=state, data=data, parent=parent, level_number=level_number)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<SkinLevelBundle display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bundle: BundleItemOfferPayload) -> Optional[Self]:
        skin_level = state.get_skin_level(data_bundle['BundleItemOfferID'])
        if skin_level is None:
            return None
        return cls(
            state=state,
            data=skin_level._data,
            parent=skin_level.parent,
            level_number=skin_level.level_number,
            data_bundle=data_bundle,
        )
