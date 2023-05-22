from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from valorantx.valorant_api.models.weapons import (
    AdsStats as AdsStats,
    AirBurstStats as AirBurstStats,
    AltShotgunStats as AltShotgunStats,
    DamageRange as DamageRange,
    Skin as SkinValorantAPI,
    SkinChroma as SkinChromaValorantAPI,
    SkinLevel as SkinLevelValorantAPI,
    Weapon as WeaponValorantAPI,
    WeaponStats as WeaponStats,
)

from .abc import BonusItemOffer, BundleItemOffer, Item, ItemOffer

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.weapons import (
        Skin as ValorantAPISkinPayload,
        SkinChroma as ValorantAPISkinChromaPayload,
        SkinLevel as ValorantAPISkinLevelPayload,
        Weapon as ValorantAPIWeaponPayload,
    )

    from ..types.store import (
        BonusStoreOffer as BonusStoreOfferPayload,
        BundleItemOffer as BundleItemOfferPayload,
        Offer as OfferPayload,
    )
    from ..valorant_api_cache import CacheState

__all__ = (
    'AdsStats',
    'AirBurstStats',
    'AltShotgunStats',
    'DamageRange',
    'Skin',
    'SkinChroma',
    'SkinLevel',
    'SkinLevelBonus',
    'SkinLevelBundle',
    'SkinLevelNightmarket',
    'SkinLevelOffer',
    'Weapon',
)


class Weapon(WeaponValorantAPI, Item):
    if TYPE_CHECKING:
        _state: CacheState

    def __init__(self, *, state: CacheState, data: ValorantAPIWeaponPayload, favorite: bool = False) -> None:
        super().__init__(state=state, data=data)
        self.skins: List[Skin] = [Skin(state=state, data=skin, parent=self) for skin in data['skins']]
        self._is_favorite: bool = favorite
        Item.__init__(self)

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, weapon: Self) -> Self:
        self = super()._copy(weapon)
        self._cost = weapon._cost
        self._is_favorite = weapon._is_favorite
        return self


class Skin(SkinValorantAPI['Weapon'], Item):
    if TYPE_CHECKING:
        _state: CacheState
        parent: Weapon

    def __init__(self, *, state: CacheState, data: ValorantAPISkinPayload, parent: Weapon, favorite: bool = False) -> None:
        super().__init__(state=state, data=data, parent=parent)
        self.chromas: List[SkinChroma] = [SkinChroma(state=state, data=chroma, parent=self) for chroma in data['chromas']]
        self.levels: List[SkinLevel] = [
            SkinLevel(state=state, data=level, parent=self, level_number=index) for index, level in enumerate(data['levels'])
        ]
        self._is_favorite: bool = favorite
        Item.__init__(self)

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, skin: Self) -> Self:
        self = super()._copy(skin)
        self._cost = skin._cost
        self._is_favorite = skin._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, skin: Self, favorite: bool) -> Self:
        self = skin._copy(skin)
        self._is_favorite = favorite
        return self


class SkinLevel(SkinLevelValorantAPI['Skin'], Item):
    if TYPE_CHECKING:
        _state: CacheState

    def __init__(
        self,
        *,
        state: CacheState,
        data: ValorantAPISkinLevelPayload,
        parent: Skin,
        level_number: int,
        favorite: bool = False,
    ) -> None:
        super().__init__(state=state, data=data, parent=parent, level_number=level_number)
        self._is_favorite: bool = favorite
        Item.__init__(self)

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, skin_level: Self) -> Self:
        self = super()._copy(skin_level)
        self._cost = skin_level._cost
        self._is_favorite = skin_level._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, skin_level: Self, favorite: bool) -> Self:
        self = skin_level._copy(skin_level)
        self._is_favorite = favorite
        return self


class SkinChroma(SkinChromaValorantAPI['Skin'], Item):
    if TYPE_CHECKING:
        _state: CacheState

    def __init__(
        self, *, state: CacheState, data: ValorantAPISkinChromaPayload, parent: Skin, favorite: bool = False
    ) -> None:
        super().__init__(state=state, data=data, parent=parent)
        self._is_favorite: bool = favorite
        Item.__init__(self)

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, skin_chroma: Self) -> Self:
        self = super()._copy(skin_chroma)
        self._cost = skin_chroma._cost
        self._is_favorite = skin_chroma._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, skin_chroma: Self, favorite: bool) -> Self:
        self = skin_chroma._copy(skin_chroma)
        self._is_favorite = favorite
        return self


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


class SkinLevelBonus(SkinLevel, BonusItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: ValorantAPISkinLevelPayload,
        parent: Skin,
        level_number: int,
        data_bonus: BonusStoreOfferPayload,
    ) -> None:
        SkinLevel.__init__(self, state=state, data=data, parent=parent, level_number=level_number)
        BonusItemOffer.__init__(self, data=data_bonus)

    def __repr__(self) -> str:
        return f'<SkinLevelNightmarket display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bonus: BonusStoreOfferPayload) -> Optional[Self]:
        skin_level = state.get_skin_level(data_bonus['Offer']['OfferID'])
        if skin_level is None:
            return None
        return cls(
            state=state,
            data=skin_level._data,
            parent=skin_level.parent,
            level_number=skin_level.level_number,
            data_bonus=data_bonus,
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
    def from_bundle(cls, *, skin_level: SkinLevel, data: BundleItemOfferPayload) -> Self:
        skin_level = skin_level._copy(skin_level)
        return cls(
            state=skin_level._state,
            data=skin_level._data,
            parent=skin_level.parent,
            level_number=skin_level.level_number,
            data_bundle=data,
        )


SkinLevelNightmarket = SkinLevelBonus
