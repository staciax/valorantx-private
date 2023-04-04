from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Union  # overload

from .. import utils
from ..asset import Asset
from ..enums import MELEE_WEAPON_ID, ItemType, Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    from ..cache import CacheState
    from ..types.weapons import (
        AdsStats as AdsStatsPayload,
        AirBurstStats as AirBurstStatsPayload,
        AltShotgunStats as AltShotgunStatsPayload,
        DamageRange as DamageRangePayload,
        GridPosition as GridPositionPayload,
        ShopData as ShopDataPayload,
        Skin as SkinPayload,
        SkinChroma as SkinChromaPayload,
        SkinLevel as SkinLevelPayload,
        Weapon as WeaponPayload,
        WeaponStats as WeaponStatsPayload,
    )

    # from .themes import Theme
    # from .content_tiers import ContentTier

__all__ = (
    'Skin',
    'SkinChroma',
    'SkinLevel',
    'Weapon',
)

# TODO: patch 6.x support variants favorites colors of skins


class GridPosition:
    def __init__(self, data: GridPositionPayload) -> None:
        self.row: float = data['row']
        self.column: float = data['column']

    def __repr__(self) -> str:
        return f"<GridPosition row={self.row} column={self.column}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, GridPosition) and self.row == other.row and self.column == other.column

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class AdsStats:
    def __init__(self, data: AdsStatsPayload) -> None:
        self.zoom_multiplier: float = data['zoomMultiplier']
        self.fire_rate: float = data['fireRate']
        self.run_speed_multiplier: float = data['runSpeedMultiplier']
        self.burst_count: float = data['burstCount']
        self.first_bullet_accuracy: float = data['firstBulletAccuracy']

    def __repr__(self) -> str:
        attrs = [
            ('zoom_multiplier', self.zoom_multiplier),
            ('fire_rate', self.fire_rate),
            ('run_speed_multiplier', self.run_speed_multiplier),
            ('burst_count', self.burst_count),
            ('first_bullet_accuracy', self.first_bullet_accuracy),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'


class AltShotgunStats:
    def __init__(self, data: AltShotgunStatsPayload) -> None:
        self.shotgun_pellet_count: float = data['shotgunPelletCount']
        self.burst_rate: float = data['burstRate']

    def __repr__(self) -> str:
        return f"<AltShotgunStats shotgun_pellet_count={self.shotgun_pellet_count} burst_rate={self.burst_rate}>"


class AirBurstStats:
    def __init__(self, data: AirBurstStatsPayload) -> None:
        self.shotgun_pellet_count: float = data['shotgunPelletCount']
        self.burst_distance: float = data['burstDistance']

    def __repr__(self) -> str:
        return f"<AirBurstStats shotgun_pellet_count={self.shotgun_pellet_count} burst_distance={self.burst_distance}>"


class DamageRange:
    def __init__(self, data: DamageRangePayload) -> None:
        self.range_start_meters: float = data['rangeStartMeters']
        self.range_end_meters: float = data['rangeEndMeters']
        self.head_damage: float = data['headDamage']
        self.body_damage: float = data['bodyDamage']
        self.leg_damage: float = data['legDamage']

    def __repr__(self) -> str:
        attrs = [
            ('range_start_meters', self.range_start_meters),
            ('range_end_meters', self.range_end_meters),
            ('head_damage', self.head_damage),
            ('body_damage', self.body_damage),
            ('leg_damage', self.leg_damage),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'


class WeaponStats:
    def __init__(self, data: WeaponStatsPayload) -> None:
        self.fire_rate: float = data.get('fireRate', 0)
        self.magazine_size: int = data.get('magazineSize', 0)
        self.run_speed_multiplier: float = data.get('runSpeedMultiplier', 0)
        self.equip_time_seconds: float = data.get('equipTimeSeconds', 0)
        self.reload_time_seconds: float = data.get('reloadTimeSeconds', 0)
        self.first_bullet_accuracy: float = data.get('firstBulletAccuracy', 0)
        self.shotgun_pellet_count: int = data.get('shotgunPelletCount', 0)
        self._wall_penetration: Optional[str] = data.get('wallPenetration')
        self._feature: Optional[str] = data.get('feature')
        self._fire_mode: Optional[str] = data.get('fireMode')
        self._alt_fire_type: Optional[str] = data.get('altFireType')
        self.ads_stats: Optional[AdsStats] = AdsStats(data['adsStats']) if data.get('adsStats') else None
        self.alt_shotgun_stats: AltShotgunStats = AltShotgunStats(data['altShotgunStats'])
        self.air_burst_stats: AirBurstStats = AirBurstStats(data['airBurstStats'])
        self.damage_ranges: List[DamageRange] = [DamageRange(x) for x in data['damageRanges']]

    def __repr__(self) -> str:
        attrs = [
            ('fire_rate', self.fire_rate),
            ('magazine_size', self.magazine_size),
            ('run_speed_multiplier', self.run_speed_multiplier),
            ('equip_time_seconds', self.equip_time_seconds),
            ('reload_time_seconds', self.reload_time_seconds),
            ('first_bullet_accuracy', self.first_bullet_accuracy),
            ('shotgun_pellet_count', self.shotgun_pellet_count),
            ('wall_penetration', self.wall_penetration),
            ('feature', self.feature),
            ('fire_mode', self.fire_mode),
            ('alt_fire_type', self.alt_fire_type),
            ('ads_stats', self.ads_stats),
            ('alt_shotgun_stats', self.alt_shotgun_stats),
            ('air_burst_stats', self.air_burst_stats),
            ('damage_ranges', self.damage_ranges),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def fire_mode(self) -> Optional[str]:
        if self._fire_mode is not None:
            return utils.removeprefix(self._fire_mode, 'EWeaponFireModeDisplayType::')
        return None

    @property
    def wall_penetration(self) -> Optional[str]:
        if self._wall_penetration is not None:
            return utils.removeprefix(self._wall_penetration, 'EWallPenetrationDisplayType::')
        return None

    @property
    def feature(self) -> Optional[str]:
        if self._feature is not None:
            return utils.removeprefix(self._feature, 'WeaponStatsFeature::')
        return None

    @property
    def alt_fire_type(self) -> Optional[str]:
        if self._alt_fire_type is not None:
            return utils.removeprefix(self._alt_fire_type, 'EWeaponAltFireDisplayType::')
        return None


class ShopData:
    def __init__(self, *, state: CacheState, weapon: Weapon, data: ShopDataPayload) -> None:
        self._weapon: Weapon = weapon
        self._state: CacheState = state
        self.cost: int = data['cost']
        self.category: Optional[str] = data['category']
        self._category_text: Union[str, Dict[str, str]] = data['categoryText']
        self._grid_position = data.get('gridPosition')
        self._can_be_trashed: bool = data['canBeTrashed']
        self._image: Optional[str] = data['image']
        self._new_image: Optional[str] = data['newImage']
        self._new_image_2: Optional[str] = data['newImage2']
        self.asset_path: str = data['assetPath']
        self._category_text_localized: Localization = Localization(self._category_text, locale=self._state.locale)
        # if self._client is not None:
        #     self._weapon.cost = self.cost

    def __repr__(self) -> str:
        return f"<ShopData category_text={self.category_text} cost={self.cost}>"

    def __int__(self) -> int:
        return self.cost

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ShopData) and self._weapon == other._weapon and self.cost == other.cost

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def grid_position(self) -> Optional[GridPosition]:
        return GridPosition(self._grid_position) if self._grid_position else None

    def category_text_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._category_text_localized.from_locale(locale)

    @property
    def category_text(self) -> Localization:
        """:class: `str` Returns the weapon's shop category text."""
        return self._category_text_localized

    def can_be_trashed(self) -> bool:
        """:class: `bool` Returns whether the weapon can be trashed."""
        return self._can_be_trashed

    @property
    def image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's image."""
        return Asset._from_url(self._state, url=self._image) if self._image else None

    @property
    def new_image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's new image."""
        return Asset._from_url(self._state, url=self._new_image) if self._new_image else None

    @property
    def new_image_2(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's new image 2."""
        return Asset._from_url(self._state, url=self._new_image_2) if self._new_image_2 else None


# --- end sub modules ---


class Weapon(BaseModel):
    def __init__(self, *, state: CacheState, data: WeaponPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._category: str = data['category']
        self.default_skin_uuid: str = data['defaultSkinUuid']
        self._display_icon: str = data['displayIcon']
        self._kill_stream_icon: str = data['killStreamIcon']
        self.asset_path: str = data['assetPath']
        self._stats: WeaponStatsPayload = data['weaponStats']
        self.shop_data: ShopData = ShopData(state=self._state, weapon=self, data=data['shopData'])
        self._cost: int = 0
        self._skins: List[SkinPayload] = data['skins']
        self.type: ItemType = ItemType.weapon
        self._is_melee: bool = True if self.uuid == str(MELEE_WEAPON_ID) else False
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f"<Weapon display_name={self.display_name!r}>"

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the weapon's name."""
        return self._display_name_localized

    @property
    def category(self) -> str:
        """:class: `str` Returns the weapon's category."""
        #  self._category.removeprefix("EEquippableCategory::")
        return utils.removeprefix(self._category, "EEquippableCategory::")

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the weapon's icon."""
        return Asset._from_url(self._state, self._display_icon)

    @property
    def kill_stream_icon(self) -> Asset:
        """:class: `Asset` Returns the weapon's kill stream icon."""
        return Asset._from_url(self._state, self._kill_stream_icon)

    @property
    def stats(self) -> WeaponStats:
        """:class: `dict` Returns the weapon's stats."""
        return WeaponStats(self._stats)

    @property
    def cost(self) -> int:
        """:class: `int` Returns the weapon's cost."""
        return self._cost

    @cost.setter
    def cost(self, value: int) -> None:
        self._cost = value

    @property
    def price(self) -> int:
        """:class: `int` Returns the weapon's price."""
        return self.cost

    # @property
    # def shop_data(self) -> Optional[ShopData]:
    #     """:class: `ShopData` Returns the weapon's shop data."""
    #     return ShopData(state=self._state, weapon=self, data=self._shop_data) if self._shop_data else None

    # @property
    # def skins(self) -> List[Skin]:
    #     """:class: `list` Returns the weapon's skins."""
    #     return [Skin(client=self._state, data=skin) for skin in self._skins]

    def is_melee(self) -> bool:
        """:class: `bool` Returns whether the weapon is a melee weapon."""
        return self._is_melee

    # def get_skins(self) -> List[Skin]:
    #     """:class: `list` Returns the weapon's skins."""
    #     return self.skins

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the weapon with the given UUID."""
    #     data = client._assets.get_weapon(uuid)
    #     return cls(client=client, data=data) if data else None


class Skin(BaseModel):
    def __init__(self, *, state: CacheState, data: SkinPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        # self._base_weapon_uuid: Optional[str] = data.get('WeaponID')
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._theme_uuid: str = data['themeUuid']
        self._content_tier_uuid: Optional[str] = data['contentTierUuid']
        self._display_icon: str = data['displayIcon']
        self._wallpaper: Optional[str] = data['wallpaper']
        self.asset_path: str = data['assetPath']
        self._chromas: List[SkinChroma] = [SkinChroma(state=self._state, data=chroma) for chroma in data['chromas']]
        self._levels: List[SkinLevel] = [SkinLevel(state=self._state, data=level) for level in data['levels']]
        # self._price: int = 0
        self.type: ItemType = ItemType.skin
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f"<Skin display_name={self.display_name!r}>"

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the skin's name."""
        return self._display_name_localized

    # @property
    # def theme(self) -> Optional[Theme]:
    #     """:class: `Theme` Returns the skin's theme uuid."""
    #     return self._client.get_theme(uuid=self._theme_uuid)

    # @property
    # def rarity(self) -> Optional[ContentTier]:
    #     """:class: `ContentTier` Returns the skin's rarity."""
    #     return self._client.get_content_tier(uuid=self._content_tier_uuid) if self._content_tier_uuid else None

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        display_icon = self._display_icon or (self.levels[0].display_icon if len(self.levels) > 0 else None)
        if display_icon is None:
            return None
        return Asset._from_url(self._state, str(display_icon))

    @property
    def wallpaper(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's wallpaper."""
        if self._wallpaper is None:
            return None
        return Asset._from_url(self._state, url=self._wallpaper)

    @property
    def chromas(self) -> List[SkinChroma]:
        """:class: `list` Returns the skin's chromas."""
        return self._chromas

    @property
    def levels(self) -> List[SkinLevel]:
        """:class: `list` Returns the skin's levels."""
        return self._levels

    # def get_weapon(self) -> Optional[Weapon]:
    #     """:class: `Weapon` Returns the skin's base weapon."""
    #     return self._client.get_weapon(uuid=self._base_weapon_uuid) if self._base_weapon_uuid else None

    # @property
    # def price(self) -> int:
    #     """:class: `int` Returns the skin's price."""
    #     if self._price == 0:
    #         if len(self.levels) > 0:
    #             self.price = self.levels[0]._price
    #     return self.price

    # @price.setter
    # def price(self, value: int) -> None:
    #     self._price = value

    # def is_melee(self) -> bool:
    #     """:class: `bool` Returns whether the bundle is a melee."""
    #     weapon = self.get_weapon()
    #     return weapon.is_melee() if weapon else False

    def get_skin_level(self, level: int) -> Optional[SkinLevel]:
        """get the skin's level with the given level.

        Parameters
        ----------
        level: :class: `int`
            The level of the skin level to get.

        Returns
        -------
        Optional[:class: `SkinLevel`]
            The skin level with the given level.
        """
        return next((skin_level for skin_level in self.levels if skin_level.level_number == level), None)

    # @classmethod
    # @overload
    # def _from_uuid(cls, client: Client, uuid: str, all_type: bool = True) -> Optional[Union[Self, SkinLevel, SkinChroma]]:
    #     ...

    # @classmethod
    # @overload
    # def _from_uuid(cls, client: Client, uuid: str, all_type: bool = False) -> Union[Self, SkinLevel, SkinChroma]:
    #     ...

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str, all_type: bool = False) -> Optional[Union[Self, SkinLevel, SkinChroma]]:
    #     """Returns the skin with the given UUID."""
    #     data = client._assets.get_skin(uuid)
    #     if not all_type and data is not None:
    #         return cls(client=client, data=data)
    #     else:
    #         return client.get_skin_level(uuid) or client.get_skin_chroma(uuid)


class SkinChroma(BaseModel):
    def __init__(self, *, state: CacheState, data: SkinChromaPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        # self._base_weapon_uuid: Optional[str] = data.get('WeaponID')
        # self._base_skin_uuid: Optional[str] = data.get('SkinID')
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: str = data['displayIcon']
        self._full_render: str = data['fullRender']
        self._swatch: Optional[str] = data['swatch']
        self._streamed_video: Optional[str] = data['streamedVideo']
        self.asset_path: str = data['assetPath']
        # self._price: int = 0
        self.type: ItemType = ItemType.skin_chroma
        # self._base_weapon: Optional[Weapon] = (
        #     self._client.get_weapon(uuid=self._base_weapon_uuid) if self._base_weapon_uuid else None
        # )
        # self._base_skin: Optional[Skin] = (
        #     self._client.get_skin(uuid=self._base_skin_uuid, level=False, chroma=False) if self._base_skin_uuid else None
        # )
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f"<SkinChroma display_name={self.display_name!r}>"

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        """Returns the skin's display name localized to the given locale."""
        return self._display_name_localized.from_locale(locale=locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the skin's name."""
        return self._display_name_localized

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        # base_skin = self.get_skin()
        # display_icon = self._display_icon or (base_skin.display_icon if base_skin else None)
        # weapon = self.get_weapon()
        # if weapon is not None:
        #     if utils.removeprefix(self.display_name.locale, 'Standard ') == weapon.display_name:
        #         display_icon = weapon.display_icon or display_icon
        # return Asset._from_url(self._state, url=str(display_icon)) if display_icon else None

    @property
    def display_icon_full_render(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon full render."""
        if self._full_render is None:
            return None
        return Asset._from_url(self._state, url=self._full_render)

    @property
    def swatch(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's swatch."""
        if self._swatch is None:
            return None
        return Asset._from_url(self._state, url=self._swatch)

    @property
    def video(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's video."""
        if self._streamed_video is None:
            return None
        return Asset._from_url(self._state, url=self._streamed_video)

    # def get_weapon(self) -> Optional[Weapon]:
    #     """:class: `Weapon` Returns the skin's base weapon."""
    #     return self._base_weapon

    # def get_skin(self) -> Optional[Skin]:
    #     """:class: `Skin` Returns the skin's base skin."""
    #     return self._base_skin

    # @property
    # def theme(self) -> Optional[Theme]:
    #     """:class: `Theme` Returns the skin's theme uuid."""
    #     return self._base_skin.theme if self._base_skin else None

    # @property
    # def rarity(self) -> Optional[ContentTier]:
    #     """:class: `ContentTier` Returns the skin's rarity."""
    #     return self._base_skin.rarity if self._base_skin else None

    # @property
    # def price(self) -> Optional[int]:
    #     """:class: `int` Returns the skin's price."""
    #     if self._price == 0:
    #         if self._base_skin is not None:
    #             self._price = self._base_skin.price
    #     return self._price

    # @price.setter
    # def price(self, value: int) -> None:
    #     self._price = value

    # def is_melee(self) -> bool:
    #     """:class: `bool` Returns whether the bundle is a melee."""
    #     return self._base_weapon.is_melee() if self._base_weapon else False

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the skin with the given UUID."""
    #     data = client._assets.get_skin_chroma(uuid)
    #     return cls(client=client, data=data) if data else None


class SkinLevel(BaseModel):
    def __init__(self, *, state: CacheState, data: SkinLevelPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        # self._base_weapon_uuid: Optional[str] = data.get('WeaponID')
        # self._base_skin_uuid: Optional[str] = data.get('SkinID')
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._level: Optional[str] = data['levelItem']
        self._display_icon: str = data['displayIcon']
        self._streamed_video: Optional[str] = data['streamedVideo']
        self.asset_path: str = data['assetPath']
        # self._price: int = self._client.get_item_price(self.uuid)
        self.level_number: int = data.get('levelNumber', 0)
        self._is_level_one: bool = self.level_number == 1
        self.type: ItemType = ItemType.skin_level
        # self._base_weapon: Optional[Weapon] = (
        #     self._client.get_weapon(uuid=self._base_weapon_uuid) if self._base_weapon_uuid else None
        # )
        # self._base_skin: Optional[Skin] = (
        #     self._client.get_skin(uuid=self._base_skin_uuid, level=False, chroma=False) if self._base_skin_uuid else None
        # )
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return str(self.display_name)

    def __repr__(self) -> str:
        return f"<SkinLevel display_name={self.display_name!r} level={self.level!r}>"

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale=locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the skin's name."""
        return self._display_name_localized

    @property
    def level(self) -> str:
        """:class: `str` Returns the skin's level."""
        if self._level is None:
            return 'Normal'
        return utils.removeprefix(self._level, 'EEquippableSkinLevelItem::')

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        # display_icon = (
        #     self._display_icon
        #     or (self._base_skin.display_icon if self._base_skin else None)
        #     or (self._base_weapon.display_icon if self._base_weapon else None)
        # )
        # return Asset._from_url(client=self._client, url=str(display_icon)) if display_icon else None

    @property
    def video(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's video."""
        if self._streamed_video is None:
            return None
        return Asset._from_url(self._state, url=self._streamed_video)

    # def get_weapon(self) -> Optional[Weapon]:
    #     """:class: `Weapon` Returns the skin's base weapon."""
    #     return self._base_weapon

    # def get_skin(self) -> Optional[Skin]:
    #     """:class: `Skin` Returns the skin's base skin."""
    #     return self._base_skin

    # @property
    # def theme(self) -> Optional[Theme]:
    #     """:class: `Theme` Returns the skin's theme uuid."""
    #     return self._base_skin.theme if self._base_skin else None

    # @property
    # def rarity(self) -> Optional[ContentTier]:
    #     """:class: `ContentTier` Returns the skin's rarity."""
    #     return self._base_skin.rarity if self._base_skin else None

    def is_level_one(self) -> bool:
        """:class: `bool` Returns whether the skin is level one."""
        return self._is_level_one

    # def is_melee(self) -> bool:
    #     """:class: `bool` Returns whether the bundle is a melee."""
    #     return self._base_weapon.is_melee() if self._base_weapon is not None else False

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the skin with the given UUID."""
    #     data = client._assets.get_skin_level(uuid)
    #     return cls(client=client, data=data) if data else None


# class SkinNightMarket(SkinLevel):
#     def __init__(self, *, client: Client, data: Mapping[str, Any], extras: Any) -> None:
#         super().__init__(client=client, data=data)
#         self.discount_percent: int = extras['DiscountPercent']
#         self._price: int = extras['Offer']['Cost'][str(CurrencyType.valorant)]
#         self.discount_price: int = extras['DiscountCosts'][str(CurrencyType.valorant)]
#         self._is_direct_purchase: bool = extras['Offer']['IsDirectPurchase']
#         self._is_seen: bool = extras['IsSeen']
#         self._rewards: List[Dict[str, Any]] = extras['Offer']['Rewards']
#         self._start_time_iso: str = extras['Offer']['StartDate']

#     def __repr__(self) -> str:
#         return f"<SkinNightMarket display_name={self.display_name!r} price={self.price!r} discount_price={self.discount_price!r}>"

#     def is_seen(self) -> bool:
#         """Returns whether the skin is seen."""
#         return self._is_seen

#     def is_direct_purchase(self) -> bool:
#         """Returns whether the skin is direct purchase."""
#         return self._is_direct_purchase

#     @property
#     def price_difference(self) -> int:
#         """Returns the difference between the base price and the discounted price"""
#         return self.price_difference - self.discount_price

#     @property
#     def start_time(self) -> datetime.datetime:
#         """Returns the time the offer started"""
#         return utils.parse_iso_datetime(self._start_time_iso)

#     # @classmethod
#     # def _from_data(cls, client: Client, skin_data: BonusStoreOfferPayload) -> Self:
#     #     """Returns the skin with the given UUID."""
#     #     uuid = skin_data['Offer']['OfferID']  # type: ignore
#     #     data = client._assets.get_skin_level(uuid)
#     #     if data is None:
#     #         raise ValueError(f'Invalid skin UUID: {uuid}')
#     #     return cls(client=client, data=data, extras=skin_data)


# class SkinBundle(SkinLevel, FeaturedBundleItem):
#     def __init__(
#         self, *, client: Client, data: Mapping[str, Any], bundle: Union[FeaturedBundleItemPayload, Dict[str, Any]]
#     ) -> None:
#         super().__init__(client=client, data=data, bundle=bundle)

#     def __repr__(self) -> str:
#         attrs = [('display_name', self.display_name), ('price', self.price), ('discounted_price', self.discounted_price)]
#         joined = ' '.join('%s=%r' % t for t in attrs)
#         return f'<{self.__class__.__name__} {joined}>'

#     @classmethod
#     def _from_bundle(cls, client: Client, uuid: str, bundle: Dict[str, Any]) -> Optional[Self]:
#         """Returns the spray level with the given UUID."""
#         data = client._assets.get_skin_level(uuid)
#         return cls(client=client, data=data, bundle=bundle) if data else None
