from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from valorant.models.weapons import (
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
    from valorant.types.weapons import (
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
        self._data = data
        super().__init__(state=state, data=data)
        self.skins: List[Skin] = [Skin(state=state, data=skin, parent=self) for skin in data['skins']]
        self._is_favorite: bool = favorite
        Item.__init__(self)

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, weapon: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = weapon._uuid
        self._state = weapon._state
        self._data = weapon._data.copy()
        self._display_name = weapon._display_name
        self.category = weapon.category
        self._default_skin_uuid = weapon._default_skin_uuid
        self._display_icon = weapon._display_icon
        self._kill_stream_icon = weapon._kill_stream_icon
        self.asset_path = weapon.asset_path
        self.weapon_stats = weapon.weapon_stats
        self.shop_data = weapon.shop_data
        self.skins = weapon.skins
        self._is_melee = weapon._is_melee
        self._display_name_localized = weapon._display_name_localized
        self._cost = weapon._cost
        self._is_favorite = weapon._is_favorite
        return self


class Skin(SkinValorantAPI, Item):
    _state: CacheState
    parent: Weapon

    def __init__(self, *, state: CacheState, data: ValorantAPISkinPayload, parent: Weapon, favorite: bool = False) -> None:
        self._data = data
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
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = skin._uuid
        self._state = skin._state
        self._data = skin._data.copy()
        self._display_name = skin._display_name
        self.theme_uuid = skin.theme_uuid
        self.content_tier_uuid = skin.content_tier_uuid
        self._display_icon = skin._display_icon
        self._wallpaper = skin._wallpaper
        self.asset_path = skin.asset_path
        self.chromas = skin.chromas.copy()
        self.levels = skin.levels.copy()
        self.parent = skin.parent
        self._display_name_localized = skin._display_name_localized
        self._cost = skin._cost
        self._is_favorite = skin._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, skin: Self, favorite: bool) -> Self:
        self = skin._copy(skin)
        self._is_favorite = favorite
        return self


class SkinLevel(SkinLevelValorantAPI, Item):
    _state: CacheState
    parent: Skin

    def __init__(
        self,
        *,
        state: CacheState,
        data: ValorantAPISkinLevelPayload,
        parent: Skin,
        level_number: int,
        favorite: bool = False,
    ) -> None:
        self._data = data
        super().__init__(state=state, data=data, parent=parent, level_number=level_number)
        self._is_favorite: bool = favorite
        Item.__init__(self)

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, skin_level: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = skin_level._uuid
        self._state = skin_level._state
        self._data = skin_level._data.copy()
        self._display_name = skin_level._display_name
        self.level_item = skin_level.level_item
        self._display_icon = skin_level._display_icon
        self._streamed_video = skin_level._streamed_video
        self.asset_path = skin_level.asset_path
        self._level_number = skin_level._level_number
        self._is_level_one = skin_level._is_level_one
        self.parent = skin_level.parent._copy(skin_level.parent)
        self._display_name_localized = skin_level._display_name_localized
        self._cost = skin_level._cost
        self._is_favorite = skin_level._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, skin_level: Self, favorite: bool) -> Self:
        self = skin_level._copy(skin_level)
        self._is_favorite = favorite
        return self


class SkinChroma(SkinChromaValorantAPI, Item):
    _state: CacheState
    parent: Skin

    def __init__(
        self, *, state: CacheState, data: ValorantAPISkinChromaPayload, parent: Skin, favorite: bool = False
    ) -> None:
        self._data = data
        super().__init__(state=state, data=data, parent=parent)
        self._is_favorite: bool = favorite
        Item.__init__(self)

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, skin_chroma: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = skin_chroma._uuid
        self._state = skin_chroma._state
        self._data = skin_chroma._data.copy()
        self._display_name = skin_chroma._display_name
        self._display_icon = skin_chroma._display_icon
        self._full_render = skin_chroma._full_render
        self._swatch = skin_chroma._swatch
        self._streamed_video = skin_chroma._streamed_video
        self.asset_path = skin_chroma.asset_path
        self.parent = skin_chroma.parent
        self._display_name_localized = skin_chroma._display_name_localized
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
        return f'<SkinLevelBundle display_name={self.display_name.default!r}>'

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
