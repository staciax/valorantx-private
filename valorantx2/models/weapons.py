from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ..valorant_api.models.weapons import (
    Skin as SkinValorantAPI,
    SkinChroma as SkinChromaValorantAPI,
    SkinLevel as SkinLevelValorantAPI,
    Weapon as WeaponValorantAPI,
)
from .abc import BundleItemOffer, _Cost

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.store import ItemOffer as ItemOfferPayload
    from ..valorant_api.types.weapons import (
        Skin as ValorantAPISkinPayload,
        SkinChroma as ValorantAPISkinChromaPayload,
        SkinLevel as ValorantAPISkinLevelPayload,
        Weapon as ValorantAPIWeaponPayload,
    )
    from ..valorant_api_cache import CacheState


class Weapon(WeaponValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: ValorantAPIWeaponPayload) -> None:
        super().__init__(state=state, data=data)


class Skin(SkinValorantAPI['Weapon'], _Cost):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinPayload, parent: Weapon) -> None:
        super().__init__(state=state, data=data, parent=parent)


class SkinLevel(SkinLevelValorantAPI['Skin'], _Cost):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinLevelPayload, parent: Skin, level_number: int) -> None:
        super().__init__(state=state, data=data, parent=parent, level_number=level_number)


class SkinChroma(SkinChromaValorantAPI['Skin'], _Cost):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinChromaPayload, parent: Skin) -> None:
        super().__init__(state=state, data=data, parent=parent)


class SkinLevelBundle(SkinLevel, BundleItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: ValorantAPISkinLevelPayload,
        parent: Skin,
        level_number: int,
        data_bundle: ItemOfferPayload,
    ) -> None:
        SkinLevel.__init__(self, state=state, data=data, parent=parent, level_number=level_number)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<SkinLevelBundle display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bundle: ItemOfferPayload) -> Optional[Self]:
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
