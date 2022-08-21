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

from .base import BaseModel

from ..asset import Asset
from ..enums import CurrencyID
from ..localization import Localization
from .. import utils

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING, Literal, overload

if TYPE_CHECKING:
    import datetime
    from typing_extensions import Self
    from ..client import Client

__all__ = (
    'Weapon',
    'Skin',
    'SkinChroma',
    'SkinLevel',
    'SkinNightMarket',
)

class Weapon(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Weapon name={self.name!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._category: str = data['category']
        self.default_skin_uuid: str = data['defaultSkinUuid']
        self._display_icon: str = data['displayIcon']
        self._kill_stream_icon: str = data['killStreamIcon']
        self.asset_path: str = data['assetPath']
        self._stats: Dict[str, Any] = data['weaponStats']
        self._shop: Dict[str, Any] = data.get('shopData', None)
        if self._shop is not None:
            self._price: int = self._shop.get('cost', 0)
            self._shop_category: str = self._shop['category']
            self._shop_category_text: Union[str, Dict[str, str]] = self._shop['categoryText']
            self._grid_position: Dict[str, int] = self._shop['gridPosition']
            self._can_be_trashed: bool = self._shop['canBeTrashed']
            self._image: Optional[str] = self._shop['image']
            self._new_image: Optional[str] = self._shop['newImage']
            self._new_image_2: Optional[str] = self._shop['newImage2']
            self._shop_asset_path: str = self._shop['assetPath']
        self._skins: List[Dict[str, Any]] = data['skins']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the weapon's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
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
    def stats(self) -> Dict[str, Any]:
        """:class: `dict` Returns the weapon's stats."""
        return self._stats

    @property
    def price(self) -> int:
        """:class: `int` Returns the weapon's price."""
        return self._price

    @property
    def shop_category(self) -> str:
        """:class: `str` Returns the weapon's shop category."""
        return self._shop_category

    @property
    def shop_category_text_localizations(self) -> Localization:
        """:class: `Localization` Returns the weapon's shop category text."""
        return Localization(self._shop_category_text, locale=self._client.locale)

    @property
    def shop_category_text(self) -> str:
        """:class: `str` Returns the weapon's shop category text."""
        return self.shop_category_text_localizations.american_english

    @property
    def grid_position(self) -> Dict[str, int]:
        """:class: `dict` Returns the weapon's grid position."""
        return self._grid_position

    @property
    def can_be_trashed(self) -> bool:
        """:class: `bool` Returns whether the weapon can be trashed."""
        return self._can_be_trashed

    @property
    def image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's image."""
        return (
            Asset._from_url(client=self._client, url=self._image)
            if self._image
            else None
        )

    @property
    def new_image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's new image."""
        return (
            Asset._from_url(client=self._client, url=self._new_image)
            if self._new_image
            else None
        )

    @property
    def new_image_2(self) -> Optional[Asset]:
        """:class: `Asset` Returns the weapon's new image 2."""
        return (
            Asset._from_url(client=self._client, url=self._new_image_2)
            if self._new_image_2
            else None
        )

    @property
    def shop_asset_path(self) -> str:
        """:class: `str` Returns the weapon's shop asset path."""
        return self._shop_asset_path

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

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __repr__(self) -> str:
        return f"<Skin name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def _update(self, data: Any) -> None:
        self._uuid = data['uuid']
        self._base_weapon_uuid: str = data['base_weapon_uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._theme_uuid: str = data['themeUuid']
        self._content_tier_uuid: str = data['contentTierUuid']
        self._display_icon: str = data['displayIcon']
        self._wallpaper: Optional[str] = data['wallpaper']
        self.asset_path: str = data['assetPath']
        self._chromas: List[Dict[str, Any]] = data['chromas']
        self._levels: List[Dict[str, Any]] = data['levels']
        self.price: int = data.get('price', 0)

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def theme(self) -> str:
        """:class: `str` Returns the skin's theme uuid."""
        return self._theme_uuid

    @property
    def content_tier(self) -> str:
        """:class: `str` Returns the skin's content tier uuid."""
        return self._content_tier_uuid

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the skin's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def wallpaper(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's wallpaper."""
        return (
            Asset._from_url(client=self._client, url=self._wallpaper)
            if self._wallpaper
            else None
        )

    @property
    def chromas(self) -> List[SkinChroma]:
        """:class: `list` Returns the skin's chromas."""
        return [SkinChroma(client=self._client, data=data) for data in self._chromas]

    @property
    def levels(self) -> List[SkinLevel]:
        """:class: `list` Returns the skin's levels."""
        return [SkinLevel(client=self._client, data=data) for data in self._levels]

    @property
    def base_weapon(self) -> Weapon:
        """:class: `Weapon` Returns the skin's base weapon."""
        return Weapon._from_uuid(client=self._client, uuid=self._base_weapon_uuid)

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str, all_type: bool = False) -> Optional[Self]:
    #     """Returns the skin with the given UUID."""
    #     data = client.assets.get_skin(uuid)
    #     if not all_type:
    #         return cls(client=client, data=data)

    @classmethod
    @overload
    def _from_uuid(
            cls,
            client: Client,
            uuid: str,
            all_type: Literal[False]
    ) -> Optional[Self]:
        ...

    @classmethod
    @overload
    def _from_uuid(
            cls,
            client: Client,
            uuid: str,
            all_type: Literal[True]
    ) -> Optional[Union[Self, SkinLevel, SkinChroma]]:
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

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<SkinChroma name={self.name!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._base_weapon_uuid: str = data['base_weapon_uuid']
        self._base_skin_uuid: str = data['base_skin_uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: str = data['displayIcon']
        self._full_render: str = data['fullRender']
        self._swatch: Optional[str] = data['swatch']
        self._streamed_video: Optional[str] = data['streamedVideo']
        self.asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the skin's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def display_icon_full_render(self) -> Asset:
        """:class: `Asset` Returns the skin's icon full render."""
        return Asset._from_url(client=self._client, url=self._full_render)

    @property
    def swatch(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's swatch."""
        return (
            Asset._from_url(client=self._client, url=self._swatch)
            if self._swatch
            else None
        )

    @property
    def video(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's video."""
        return (
            Asset._from_url(client=self._client, url=self._streamed_video)
            if self._streamed_video
            else None
        )

    @property
    def base_weapon(self) -> Weapon:
        """:class: `Weapon` Returns the skin's base weapon."""
        return Weapon._from_uuid(client=self._client, uuid=self._base_weapon_uuid)

    @property
    def base_skin(self) -> Skin:
        """:class: `Skin` Returns the skin's base skin."""
        return Skin._from_uuid(client=self._client, uuid=self._base_skin_uuid)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the skin with the given UUID."""
        data = client.assets.get_skin_chroma(uuid)
        return cls(client=client, data=data) if data else None

class SkinLevel(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<SkinLevel name={self.name!r} level={self.level!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._base_weapon_uuid: str = data['base_weapon_uuid']
        self._base_skin_uuid: str = data['base_skin_uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._level: Optional[str] = data['levelItem']
        self._display_icon: str = data['displayIcon']
        self._streamed_video: Optional[str] = data['streamedVideo']
        self.asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def level(self) -> Optional[str]:
        """:class: `str` Returns the skin's level."""
        return self._level.removeprefix('EEquippableSkinLevelItem::') if self._level else None

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the skin's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def video(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's video."""
        return (
            Asset._from_url(client=self._client, url=self._streamed_video)
            if self._streamed_video
            else None
        )

    @property
    def base_weapon(self) -> Weapon:
        """:class: `Weapon` Returns the skin's base weapon."""
        return Weapon._from_uuid(client=self._client, uuid=self._base_weapon_uuid)

    @property
    def base_skin(self) -> Skin:
        """:class: `Skin` Returns the skin's base skin."""
        return Skin._from_uuid(client=self._client, uuid=self._base_skin_uuid)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the skin with the given UUID."""
        data = client.assets.get_skin_level(uuid)
        return cls(client=client, data=data) if data else None

class SkinNightMarket(SkinLevel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]], extras: Any) -> None:
        super().__init__(client=client, data=data)
        self.discount_percent: int = extras['DiscountPercent']
        self.price: int = extras['Offer']['Cost'][str(CurrencyID.valorant_point)]
        self.discount_price: int = extras['DiscountCosts'][str(CurrencyID.valorant_point)]
        self.is_direct_purchase: bool = extras['Offer']['IsDirectPurchase']
        self.is_seen: bool = extras['IsSeen']
        self._rewards: List[Dict[str, Any]] = extras['Offer']['Rewards']
        self._start_time_iso: str = extras['Offer']['StartDate']

    def __repr__(self) -> str:
        return f"<SkinNightMarket name={self.name!r} price={self.price!r} discount_price={self.discount_price!r}>"

    @property
    def price_difference(self) -> int:
        """ Returns the difference between the base price and the discounted price """
        return self.price_difference - self.discount_price

    @property
    def start_time(self) -> datetime.datetime:
        """ Returns the time the offer started """
        return utils.parse_iso_datetime(self._start_time_iso)

    @classmethod
    def _from_data(cls, client: Client, skin_data: Dict[str, Any]) -> Self:
        """Returns the skin with the given UUID."""
        uuid = skin_data['Offer']['OfferID']
        data = client.assets.get_skin_level(uuid)
        return cls(client=client, data=data, extras=skin_data)
