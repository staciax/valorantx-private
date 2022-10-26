"""
The MIT License (MIT)

Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generic, List, Mapping, Optional, TypeVar, Union, overload

from .. import utils
from ..asset import Asset
from ..enums import CurrencyID, ItemType
from ..localization import Localization
from .base import BaseFeaturedBundleItem, BaseModel

if TYPE_CHECKING:
    import datetime

    from typing_extensions import Self

    from ..client import Client
    from ..types.collection import SkinLoadout as SkinLoadoutPayload
    from ..types.store import FeaturedBundleItem as FeaturedBundleItemPayload
    from .buddy import Buddy, BuddyLevel
    from .content import ContentTier
    from .player_card import PlayerCard
    from .theme import Theme

__all__ = (
    'Skin',
    'SkinBundle',
    'SkinChroma',
    'SkinChromaLoadout',
    'SkinLevel',
    'SkinLevelLoadout',
    'SkinLoadout',
    'SkinNightMarket',
    'Weapon',
)

# --- sup models ---


class GridPosition:
    def __init__(self, data: Dict[str, Union[int, float]]) -> None:
        self.row: int = data['row']
        self.column: int = data['column']

    def __repr__(self) -> str:
        return f"<GridPosition row={self.row} column={self.column}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, GridPosition) and self.row == other.row and self.column == other.column

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class AdsStats:
    def __init__(self, data: Dict[str, Union[int, float]]) -> None:
        self.zoom_multiplier: float = data['zoomMultiplier']
        self.fire_rate: float = data['fireRate']
        self.run_speed_multiplier: float = data['runSpeedMultiplier']
        self.burst_count: int = data['burstCount']
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
    def __init__(self, data: Dict[str, Union[int, float]]) -> None:
        self.shotgun_pellet_count: int = data['shotgunPelletCount']
        self.burst_rate: float = data['burstRate']

    def __repr__(self) -> str:
        return f"<AltShotgunStats shotgun_pellet_count={self.shotgun_pellet_count} burst_rate={self.burst_rate}>"


class AirBurstStats:
    def __init__(self, data: Dict[str, Union[int, float]]) -> None:
        self.shotgun_pellet_count: int = data['shotgunPelletCount']
        self.burst_distance: float = data['burstDistance']

    def __repr__(self) -> str:
        return f"<AirBurstStats shotgun_pellet_count={self.shotgun_pellet_count} burst_distance={self.burst_distance}>"


class DamageRange:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.range_start_meters: int = data['rangeStartMeters']
        self.range_end_meters: float = data['rangeEndMeters']
        self.head_damage: float = data['headDamage']
        self.body_damage: int = data['bodyDamage']
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
    def __init__(self, data: Dict[str, Any]) -> None:
        self.fire_rate: int = data['fireRate']
        self.magazine_size: int = data['magazineSize']
        self.run_speed_multiplier: float = data['runSpeedMultiplier']
        self.equip_time_seconds: float = data['equipTimeSeconds']
        self.reload_time_seconds: int = data['reloadTimeSeconds']
        self.first_bullet_accuracy: float = data['firstBulletAccuracy']
        self.shotgun_pellet_count: int = data['shotgunPelletCount']
        self._wall_penetration: str = data['wallPenetration']
        self._feature: str = data['feature']
        self._fire_mode: Optional[str] = data['fireMode']
        self._alt_fire_type: str = data['altFireType']
        self.ads_stats: Optional[AdsStats] = AdsStats(data['adsStats']) if data.get('adsStats') else None
        self.alt_shotgun_stats: AltShotgunStats = data['altShotgunStats']
        self.air_burst_stats: AirBurstStats = data['airBurstStats']
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
    def fire_mode(self) -> str:
        return self._fire_mode.removeprefix('EWeaponFireModeDisplayType::')

    @property
    def wall_penetration(self) -> str:
        return self._wall_penetration.removeprefix('EWallPenetrationDisplayType::')

    @property
    def feature(self) -> str:
        return self._feature.removeprefix('WeaponStatsFeature::')

    @property
    def alt_fire_type(self) -> str:
        return self._alt_fire_type.removeprefix('EWeaponAltFireDisplayType::')


class ShopData:
    def __init__(self, weapon: Weapon, data: Dict[str, Any]) -> None:
        self._weapon: Weapon = weapon
        self._client: Client = getattr(weapon, '_client', None)
        self.cost: int = data['cost']
        self.category: Optional[str] = data['category']
        self._category_text: Optional[Union[str, Dict[str, str]]] = data['categoryText']
        self._grid_position = data.get('gridPosition')
        self._can_be_trashed: bool = data['canBeTrashed']
        self._image: Optional[str] = data['image']
        self._new_image: Optional[str] = data['newImage']
        self._new_image_2: Optional[str] = data['newImage2']
        self.asset_path: str = data['assetPath']
        if self._client is not None:
            self._weapon.cost = self.cost

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

    @property
    def category_text_localizations(self) -> Localization:
        """:class: `Localization` Returns the weapon's shop category text."""
        return Localization(self._category_text, locale=self._client.locale)

    @property
    def category_text(self) -> str:
        """:class: `str` Returns the weapon's shop category text."""
        return self.category_text_localizations.american_english

    def can_be_trashed(self) -> bool:
        """:class: `bool` Returns whether the weapon can be trashed."""
        return self._can_be_trashed

    @property
    def image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's image."""
        return Asset._from_url(client=self._client, url=self._image) if self._image else None

    @property
    def new_image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's new image."""
        return Asset._from_url(client=self._client, url=self._new_image) if self._new_image else None

    @property
    def new_image_2(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's new image 2."""
        return Asset._from_url(client=self._client, url=self._new_image_2) if self._new_image_2 else None


# --- end sub modules ---


class Weapon(BaseModel):
    def __init__(self, *, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._category: str = data['category']
        self.default_skin_uuid: str = data['defaultSkinUuid']
        self._display_icon: str = data['displayIcon']
        self._kill_stream_icon: str = data['killStreamIcon']
        self.asset_path: str = data['assetPath']
        self._stats: Dict[str, Any] = data['weaponStats']
        self._shop_data: Optional[Dict[str, Any]] = data.get('shopData')
        self._cost: int = 0
        self._skins: List[Dict[str, Any]] = data['skins']
        self.type: ItemType = ItemType.weapon

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<Weapon display_name={self.display_name!r}>"

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the weapon's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the weapon's name."""
        return self.name_localizations.american_english

    @property
    def category(self) -> str:
        """:class: `str` Returns the weapon's category."""
        return self._category.removeprefix("EEquippableCategory::")

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the weapon's icon."""
        return Asset._from_url(self._client, self._display_icon)

    @property
    def kill_stream_icon(self) -> Asset:
        """:class: `Asset` Returns the weapon's kill stream icon."""
        return Asset._from_url(self._client, self._kill_stream_icon)

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

    @property
    def shop_data(self) -> Optional[ShopData]:
        """:class: `ShopData` Returns the weapon's shop data."""
        return ShopData(self, self._shop_data) if self._shop_data else None

    @property
    def skins(self) -> List[Skin]:
        """:class: `list` Returns the weapon's skins."""
        return [Skin(client=self._client, data=skin) for skin in self._skins]

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the weapon with the given UUID."""
        data = client.assets.get_weapon(uuid)
        return cls(client=client, data=data) if data else None


class Skin(BaseModel):
    def __init__(self, *, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid = data['uuid']
        self._base_weapon_uuid: Optional[str] = data.get('base_weapon_uuid')
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._theme_uuid: str = data['themeUuid']
        self._content_tier_uuid: Optional[str] = data['contentTierUuid']
        self._display_icon: str = data['displayIcon']
        self._wallpaper: Optional[str] = data['wallpaper']
        self.asset_path: str = data['assetPath']
        self._chromas: List[Dict[str, Any]] = data['chromas']
        self._levels: List[Dict[str, Any]] = data['levels']
        self._price: int = 0
        self._is_favorite: bool = False
        self.type: ItemType = ItemType.skin

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<Skin display_name={self.display_name!r}>"

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def theme(self) -> Theme:
        """:class: `Theme` Returns the skin's theme uuid."""
        return self._client.get_theme(uuid=self._theme_uuid)

    @property
    def rarity(self) -> Optional[ContentTier]:
        """:class: `ContentTier` Returns the skin's rarity."""
        return self._client.get_content_tier(uuid=self._content_tier_uuid) if self._content_tier_uuid else None

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        display_icon = self._display_icon or (self.levels[0].display_icon if len(self.levels) > 0 else None)
        return Asset._from_url(self._client, str(display_icon)) if display_icon else None

    @property
    def wallpaper(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's wallpaper."""
        return Asset._from_url(client=self._client, url=self._wallpaper) if self._wallpaper else None

    @property
    def chromas(self) -> List[SkinChroma]:
        """:class: `list` Returns the skin's chromas."""
        return [SkinChroma(client=self._client, data=data) for data in self._chromas]

    @property
    def levels(self) -> List[SkinLevel]:
        """:class: `list` Returns the skin's levels."""
        return [SkinLevel(client=self._client, data=data) for data in self._levels]

    @property
    def base_weapon(self) -> Optional[Weapon]:
        """:class: `Weapon` Returns the skin's base weapon."""
        return self._client.get_weapon(uuid=self._base_weapon_uuid) if self._base_weapon_uuid else None

    @property
    def price(self) -> int:
        """:class: `int` Returns the skin's price."""
        if self._price == 0:
            if len(self.levels) > 0:
                self._price = self.levels[0].price
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    def is_favorite(self) -> bool:
        """:class: `bool` Returns whether the skin is favorited."""
        return self._is_favorite

    def set_favorite(self, value: bool) -> None:
        self._is_favorite = value

    async def add_favorite(self, *, force: bool = False) -> bool:
        """coro Adds the skin to the user's favorites."""

        if self.is_favorite() and not force:
            return False
        to_fav = await self._client.add_favorite(self)
        if self in to_fav.skins:
            self._is_favorite = True
        return self.is_favorite()

    async def remove_favorite(self, *, force: bool = False) -> bool:
        """coro Removes the skin from the user's favorites."""
        if not self.is_favorite() and not force:
            return False
        remove_fav = await self._client.remove_favorite(self)
        if self not in remove_fav.skins:
            self._is_favorite = False
        return self.is_favorite()

    @classmethod
    @overload
    def _from_uuid(cls, client: Client, uuid: str, all_type: bool = True) -> Optional[Union[Self, SkinLevel, SkinChroma]]:
        ...

    @classmethod
    @overload
    def _from_uuid(cls, client: Client, uuid: str, all_type: bool = False) -> Optional[Self]:
        ...

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str, all_type: bool = False) -> Optional[Self]:
        """Returns the skin with the given UUID."""
        data = client.assets.get_skin(uuid)
        if not all_type:
            return cls(client=client, data=data)
        else:
            return client.get_skin_level(uuid) or client.get_skin_chroma(uuid)


class SkinChroma(BaseModel):
    def __init__(self, *, client: Client, data: Mapping[str, Any], **kwargs) -> None:
        super().__init__(client=client, data=data, **kwargs)
        self._uuid: str = data['uuid']
        self._base_weapon_uuid: Optional[str] = data.get('base_weapon_uuid')
        self._base_skin_uuid: Optional[str] = data.get('base_skin_uuid')
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: str = data['displayIcon']
        self._full_render: str = data['fullRender']
        self._swatch: Optional[str] = data['swatch']
        self._streamed_video: Optional[str] = data['streamedVideo']
        self.asset_path: str = data['assetPath']
        self._price: int = 0
        self.type: ItemType = ItemType.skin_chroma

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<SkinChroma display_name={self.display_name!r}>"

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english or ''

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        if self._display_name == getattr(self.base_weapon, '_display_name'):
            display_icon = self.base_weapon.display_icon
        else:
            display_icon = self._display_icon or self.base_skin.display_icon
        return Asset._from_url(client=self._client, url=str(display_icon)) if display_icon else None

    @property
    def display_icon_full_render(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon full render."""
        return Asset._from_url(client=self._client, url=self._full_render) if self._full_render else None

    @property
    def swatch(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's swatch."""
        return Asset._from_url(client=self._client, url=self._swatch) if self._swatch else None

    @property
    def video(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's video."""
        return Asset._from_url(client=self._client, url=self._streamed_video) if self._streamed_video else None

    @property
    def base_weapon(self) -> Optional[Weapon]:
        """:class: `Weapon` Returns the skin's base weapon."""
        return self._client.get_weapon(uuid=self._base_weapon_uuid) if self._base_weapon_uuid else None

    @property
    def base_skin(self) -> Optional[Skin]:
        """:class: `Skin` Returns the skin's base skin."""
        return self._client.get_skin(uuid=self._base_skin_uuid) if self._base_skin_uuid else None

    @property
    def theme(self) -> Optional[Theme]:
        """:class: `Theme` Returns the skin's theme uuid."""
        return self.base_skin.theme if self.base_skin else None

    @property
    def rarity(self) -> Optional[ContentTier]:
        """:class: `ContentTier` Returns the skin's rarity."""
        return self.base_skin.rarity if self.base_skin else None

    @property
    def price(self) -> Optional[int]:
        """:class: `int` Returns the skin's price."""
        if self._price == 0:
            if hasattr(self.base_skin, 'price'):
                self._price = self.base_skin.price
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    def is_favorite(self) -> bool:
        """:class: `bool` Returns whether the skin is in the user's favorites."""
        return self.base_skin.is_favorite() if self.base_skin is not None else False

    def set_favorite(self, value: bool) -> None:
        if self.base_skin is not None:
            self.base_skin.set_favorite(value)

    async def add_favorite(self, *, force: bool = False) -> bool:
        """|coro|

        Parameters
        ----------
        force: :class:`bool`
            Whether to force add the skin to the user's favorites.

        Returns
        -------
        :class:`bool`
            Whether the skin was added to the user's favorites.
        """
        return await self.base_skin.add_favorite(force=force)

    async def remove_favorite(self, *, force: bool = False) -> bool:
        """|coro|

        Parameters
        ----------
        force: :class:`bool`
            Whether to force remove the skin from the user's favorites.

        Returns
        -------
        :class:`bool`
            Whether the skin was removed from the user's favorites.
        """
        return await self.base_skin.remove_favorite(force=force)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the skin with the given UUID."""
        data = client.assets.get_skin_chroma(uuid)
        return cls(client=client, data=data) if data else None


class SkinLevel(BaseModel):
    def __init__(self, *, client: Client, data: Mapping[str, Any], **kwargs) -> None:
        super().__init__(client=client, data=data, **kwargs)
        self._uuid: str = data['uuid']
        self._base_weapon_uuid: Optional[str] = data.get('base_weapon_uuid')
        self._base_skin_uuid: Optional[str] = data.get('base_skin_uuid')
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._level: Optional[str] = data.get('levelItem')
        self._display_icon: str = data['displayIcon']
        self._streamed_video: Optional[str] = data.get('streamedVideo')
        self.asset_path: str = data['assetPath']
        self._price: int = self._client.get_item_price(self.uuid)
        self._is_level_one: bool = data['isLevelOne']
        self.type: ItemType = ItemType.skin_level

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<SkinLevel display_name={self.display_name!r} level={self.level!r}>"

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def level(self) -> str:
        """:class: `str` Returns the skin's level."""
        if self._level is None:
            return 'Normal'
        return self._level.removeprefix('EEquippableSkinLevelItem::')

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        display_icon = self._display_icon or self.base_skin.display_icon or self.base_weapon.display_icon
        return Asset._from_url(client=self._client, url=str(display_icon)) if display_icon else None

    @property
    def video(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's video."""
        return Asset._from_url(client=self._client, url=self._streamed_video) if self._streamed_video else None

    @property
    def base_weapon(self) -> Optional[Weapon]:
        """:class: `Weapon` Returns the skin's base weapon."""
        return self._client.get_weapon(uuid=self._base_weapon_uuid) if self._base_weapon_uuid else None

    @property
    def base_skin(self) -> Optional[Skin]:
        """:class: `Skin` Returns the skin's base skin."""
        return self._client.get_skin(uuid=self._base_skin_uuid) if self._base_skin_uuid else None

    @property
    def theme(self) -> Optional[Theme]:
        """:class: `Theme` Returns the skin's theme uuid."""
        return self.base_skin.theme if self.base_skin else None

    @property
    def rarity(self) -> Optional[ContentTier]:
        """:class: `ContentTier` Returns the skin's rarity."""
        return self.base_skin.rarity if self.base_skin else None

    @property
    def price(self) -> Optional[int]:
        """:class: `int` Returns the skin's price."""
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    def is_level_one(self) -> bool:
        """:class: `bool` Returns whether the skin is level one."""
        return self._is_level_one

    def is_favorite(self) -> bool:
        """:class: `bool` Returns whether the skin is favorited."""
        return self.base_skin.is_favorite() if self.base_skin is not None else False

    def set_favorite(self, value: bool) -> None:
        if self.base_skin is not None:
            self.base_skin.set_favorite(value)

    async def add_favorite(self, *, force: bool = False) -> bool:
        """|coro|

        Parameters
        ----------
        force: :class:`bool`
            Whether to force add the skin to the user's favorites.

        Returns
        -------
        :class:`bool`
            Whether the skin was added to the user's favorites.
        """
        return await self.base_skin.add_favorite(force=force)

    async def remove_favorite(self, *, force: bool = False) -> bool:
        """|coro|

        Parameters
        ----------
        force: :class:`bool`
            Whether to force remove the skin from the user's favorites.

        Returns
        -------
        :class:`bool`
            Whether the skin was removed from the user's favorites.
        """
        return await self.base_skin.remove_favorite(force=force)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the skin with the given UUID."""
        data = client.assets.get_skin_level(uuid)
        return cls(client=client, data=data) if data else None


class SkinNightMarket(SkinLevel):
    def __init__(self, *, client: Client, data: Mapping[str, Any], extras: Any) -> None:
        super().__init__(client=client, data=data)
        self.discount_percent: int = extras['DiscountPercent']
        self._price: int = extras['Offer']['Cost'][str(CurrencyID.valorant_point)]
        self.discount_price: int = extras['DiscountCosts'][str(CurrencyID.valorant_point)]
        self._is_direct_purchase: bool = extras['Offer']['IsDirectPurchase']
        self._is_seen: bool = extras['IsSeen']
        self._rewards: List[Dict[str, Any]] = extras['Offer']['Rewards']
        self._start_time_iso: str = extras['Offer']['StartDate']

    def __repr__(self) -> str:
        return f"<SkinNightMarket display_name={self.display_name!r} price={self.price!r} discount_price={self.discount_price!r}>"

    def is_seen(self) -> bool:
        """Returns whether the skin is seen."""
        return self._is_seen

    def is_direct_purchase(self) -> bool:
        """Returns whether the skin is direct purchase."""
        return self._is_direct_purchase

    @property
    def price_difference(self) -> int:
        """Returns the difference between the base price and the discounted price"""
        return self.price_difference - self.discount_price

    @property
    def start_time(self) -> datetime.datetime:
        """Returns the time the offer started"""
        return utils.parse_iso_datetime(self._start_time_iso)

    @classmethod
    def _from_data(cls, client: Client, skin_data: Dict[str, Any]) -> Self:
        """Returns the skin with the given UUID."""
        uuid = skin_data['Offer']['OfferID']
        data = client.assets.get_skin_level(uuid)
        return cls(client=client, data=data, extras=skin_data)


class SkinBundle(SkinLevel, BaseFeaturedBundleItem):
    def __init__(self, *, client: Client, data: Mapping[str, Any], bundle: FeaturedBundleItemPayload) -> None:
        super().__init__(client=client, data=data, bundle=bundle)

    def __repr__(self) -> str:
        attrs = [('display_name', self.display_name), ('price', self.price), ('discounted_price', self.discounted_price)]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @classmethod
    def _from_bundle(cls, client: Client, uuid: str, bundle: Dict[str, Any]) -> Optional[Self]:
        """Returns the spray level with the given UUID."""
        data = client.assets.get_skin_level(uuid)
        return cls(client=client, data=data, bundle=bundle) if data else None


T = TypeVar('T', bound=Union['Buddy', 'PlayerCard', Skin, SkinLevel, SkinChroma])


class BaseLoadout:

    if TYPE_CHECKING:
        _client: Client

    def __init__(self, loadout: SkinLoadoutPayload, *args, **kwargs: Any) -> None:
        self._buddy_uuid = loadout.get('CharmID')
        self._buddy_level_uuid = loadout.get('CharmLevelID')
        self._is_favorite_loadout: bool = False

    def is_random(self: T) -> bool:
        """:class:`bool` Returns whether the skin is random."""
        return True if 'Random' in self.asset_path else False

    def is_favorite(self) -> bool:
        """:class: `bool` Returns whether the skin is favorited."""
        return self._is_favorite_loadout

    def set_favorite(self, value: bool) -> None:
        self._is_favorite_loadout = value

    @property
    def buddy(self) -> Optional[Buddy]:
        """Returns the buddy for this skin"""
        return self._client.get_buddy(uuid=self._buddy_uuid) if self._buddy_uuid else None

    @property
    def buddy_level(self) -> Optional[BuddyLevel]:
        """Returns the buddy level for this skin"""
        return self._client.get_buddy_level(uuid=self._buddy_level_uuid) if self._buddy_level_uuid else None


class SkinLoadout(Skin, BaseLoadout):
    def __init__(self, *, client: Client, data: Any, loadout: SkinLoadoutPayload) -> None:
        super().__init__(client=client, data=data, loadout=loadout)

    def __repr__(self) -> str:
        return f"<SkinLoadout display_name={self.display_name!r}>"

    @classmethod
    def _from_loadout(cls, client: Client, uuid: str, loadout: SkinLoadoutPayload) -> Optional[Self]:
        data = client.assets.get_skin(uuid)
        return cls(client=client, data=data, loadout=loadout) if data else None


class SkinLevelLoadout(SkinLevel, BaseLoadout):
    def __init__(self, *, client: Client, data: Any, loadout: SkinLoadoutPayload) -> None:
        super().__init__(client=client, data=data, loadout=loadout)

    def __repr__(self) -> str:
        return f"<SkinLevelLoadout display_name={self.display_name!r}>"

    @classmethod
    def _from_loadout(cls, client: Client, uuid: str, loadout: SkinLoadoutPayload) -> Self:
        data = client.assets.get_skin_level(uuid)
        return cls(client=client, data=data, loadout=loadout)


class SkinChromaLoadout(SkinChroma, BaseLoadout):
    def __init__(self, *, client: Client, data: Any, loadout: SkinLoadoutPayload) -> None:
        super().__init__(client=client, data=data, loadout=loadout)

    def __repr__(self) -> str:
        return f"<SkinChromaLoadout display_name={self.display_name!r}>"

    @classmethod
    def _from_loadout(cls, client: Client, uuid: str, loadout: SkinLoadoutPayload) -> Self:
        data = client.assets.get_skin_chroma(uuid)
        return cls(client=client, data=data, loadout=loadout)
