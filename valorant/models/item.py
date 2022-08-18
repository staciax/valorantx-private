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

from ..localization import Localization
from ..asset import Asset

from .base import BaseModel
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..client import Client

__all__ = (
    'Buddy',
    'Spray',
    'PlayerCard',
    'PlayerTitle',
    'Weapon',
    'Skin',
    'SkinChroma',
    'SkinLevel',
)

# TODO: เอาออกบาง property เป็น variable และใส่ docs ของ class เข้าไป


class Buddy(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]], bundle: Any = None) -> None:
        super().__init__(client=client, data=data, bundle=bundle)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Buddy name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._theme_uuid: Optional[str] = data.get('themeUuid')
        self._display_icon: Optional[str] = data.get('displayIcon')
        self._charm_level: int = data['charmLevel']
        self._asset_path: str = data['assetPath']
        self._price: int = data.get('price', 0)
        if self._extras.get('bundle') is not None:
            self._bundle: Any = self._extras['bundle']
            self._price: int = self._bundle.get('BasePrice', self._price)
            self._discounted_price: int = self._bundle.get('DiscountedPrice', self._price)
            self._is_promo: bool = self._bundle.get('IsPromoItem')
            self._currency_id: str = self._bundle.get('CurrencyID')
            self._discount_percent: float = self._bundle.get('DiscountPercent')

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the buddy's name."""
        return self.name_localizations.american_english

    @property
    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the buddy is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @property
    def theme(self) -> str:  # TODO: Theme Object
        """:class: `str` Returns the buddy's theme."""
        return self._theme_uuid

    @property
    def charm_level(self) -> int:
        """:class: `int` Returns the buddy's charm level."""
        return self._charm_level

    @property
    def icon(self) -> Asset:
        """:class: `Asset` Returns the buddy's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the buddy's asset path."""
        return self._asset_path

    @property
    def price(self) -> int:
        """:class: `int` Returns the buddy's price."""
        return self._price

    # bundle

    @property
    def discounted_price(self) -> int:
        """:class: `int` Returns the discounted price."""
        return self._discounted_price

    @property
    def discount_percent(self) -> float:
        """:class: `float` Returns the discount percent."""
        return self._discount_percent

    @property
    def is_promo(self) -> bool:
        """:class: `bool` Returns whether the bundle is a promo."""
        return self._is_promo


class Spray(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]], bundle: Any = None) -> None:
        super().__init__(client=client, data=data, bundle=bundle)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Spray name={self.name!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self._full_icon: Optional[str] = data['fullIcon']
        self._full_transparent_icon: Optional[str] = data['fullTransparentIcon']
        self._animation_png: Optional[str] = data['animationPng']
        self._animation_gif: Optional[str] = data['animationGif']
        self._spray_level: int = data['sprayLevel']
        self._asset_path: str = data['assetPath']
        self._price = data.get('price', 0)
        if self._extras.get('bundle') is not None:
            self._bundle: Any = self._extras['bundle']
            self._price: int = self._bundle.get('BasePrice', self._price)
            self._discounted_price: int = self._bundle.get('DiscountedPrice', self._price)
            self._is_promo: bool = self._bundle.get('IsPromoItem')
            self._currency_id: str = self._bundle.get('CurrencyID')
            self._discount_percent: float = self._bundle.get('DiscountPercent')

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        if self._full_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._full_icon)

    @property
    def full_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's full icon."""
        if self._full_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._full_icon)

    @property
    def full_transparent_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's full transparent icon."""
        if self._full_transparent_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._full_transparent_icon)

    @property
    def animation_png(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's animation png."""
        if self._animation_png is None:
            return None
        return Asset._from_url(client=self._client, url=self._animation_png)

    @property
    def animation_gif(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's animation gif."""
        if self._animation_gif is None:
            return None
        return Asset._from_url(client=self._client, url=self._animation_gif)

    @property
    def spray_level(self) -> int:
        """:class: `int` Returns the skin's spray level."""
        return self._spray_level

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the skin's asset path."""
        return self._asset_path

    @property
    def price(self) -> int:
        """:class: `int` Returns the skin's price."""
        return self._price

    # bundle

    @property
    def discounted_price(self) -> int:
        """:class: `int` Returns the discounted price."""
        return self._discounted_price

    @property
    def discount_percent(self) -> float:
        """:class: `float` Returns the discount percent."""
        return self._discount_percent

    @property
    def is_promo(self) -> bool:
        """:class: `bool` Returns whether the bundle is a promo."""
        return self._is_promo


class PlayerCard(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]], bundle: Any = None) -> None:
        super().__init__(client=client, data=data, bundle=bundle)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<PlayerCard name={self.name!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._display_icon: Optional[str] = data['displayIcon']
        self._small_icon: Optional[str] = data['smallArt']
        self._wide_icon: Optional[str] = data['wideArt']
        self._large_icon: Optional[str] = data['largeArt']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self._asset_path: str = data['assetPath']
        self._price = data.get('price', 0)
        if self._extras.get('bundle') is not None:
            self._bundle: Any = self._extras['bundle']
            self._price: int = self._bundle.get('BasePrice', self._price)
            self._discounted_price: int = self._bundle.get('DiscountedPrice', self._price)
            self._is_promo: bool = self._bundle.get('IsPromoItem')
            self._currency_id: str = self._bundle.get('CurrencyID')
            self._discount_percent: float = self._bundle.get('DiscountPercent')

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the buddy's name."""
        return self.name_localizations.american_english

    @property
    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the player card is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @property
    def icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the buddy's icon."""
        if self._display_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def small_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the buddy's small icon."""
        if self._small_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._small_icon)

    @property
    def wide_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the buddy's wide icon."""
        if self._wide_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._wide_icon)

    @property
    def large_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the buddy's large icon."""
        if self._large_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._large_icon)

    @property
    def theme_uuid(self) -> Optional[str]:
        """:class: `str` Returns the buddy's theme uuid."""
        return self._theme_uuid

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the buddy's asset path."""
        return self._asset_path

    @property
    def price(self) -> int:
        """:class: `int` Returns the buddy's price."""
        return self._price

    @property
    def discounted_price(self) -> int:
        """:class: `int` Returns the discounted price."""
        return self._discounted_price

    @property
    def discount_percent(self) -> float:
        """:class: `float` Returns the discount percent."""
        return self._discount_percent

    @property
    def is_promo(self) -> bool:
        """:class: `bool` Returns whether the buddy is a promo."""
        return self._is_promo

    @property
    def currency_id(self) -> str:
        """:class: `str` Returns the currency id."""
        return self._currency_id

    # @property
    # def is_owned(self) -> bool:
    #     """:class: `bool` Returns whether the player card is owned."""
    #     return self._client.player_cards.is_owned(self.uuid)


class PlayerTitle(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"<PlayerTitle name={self.name!r} text={self.text!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._title_text: Union[str, Dict[str, str]] = data['titleText']
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the player title's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the player title's name."""
        return self.name_localizations.american_english

    @property
    def text_localizations(self) -> Localization:
        """:class: `Translator` Returns the player title's title text."""
        return Localization(self._title_text, locale=self._client.locale)

    @property
    def text(self) -> str:
        """:class: `str` Returns the player title's title text."""
        return self.text_localizations.american_english

    @property
    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the player title is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the player title's asset path."""
        return self._asset_path


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
        self._default_skin_uuid: str = data['defaultSkinUuid']
        self._display_icon: str = data['displayIcon']
        self._kill_stream_icon: str = data['killStreamIcon']
        self._asset_path: str = data['assetPath']
        self._stats: Dict[str, Any] = data['weaponStats']
        self._shop: Dict[str, Any] = data['shopData']
        self._price: int = self._shop['cost']
        self._shop_category: str = self._shop['category']
        self._shop_category_text: Union[str, Dict[str, str]] = self._shop['categoryText']
        self._grid_position: Dict[str, int] = self._shop['gridPosition']
        self._can_be_trashed: bool = self._shop['canBeTrashed']
        self._image: Optional[str] = self._shop.get('image')
        self._new_image: Optional[str] = self._shop.get('newImage')
        self._new_image_2: Optional[str] = self._shop.get('newImage2')
        self._shop_asset_path: str = self._shop['assetPath']
        self._skins: List[Dict[str, Any]] = data['skins']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the weapon's names."""
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
    def default_skin_uuid(self) -> str:
        """:class: `str` Returns the weapon's default skin uuid."""
        return self._default_skin_uuid

    @property
    def icon(self) -> Asset:
        """:class: `Asset` Returns the weapon's icon."""
        return Asset._from_url(self._client, self._display_icon)

    @property
    def kill_stream_icon(self) -> Asset:
        """:class: `Asset` Returns the weapon's kill stream icon."""
        return Asset._from_url(self._client, self._kill_stream_icon)

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the weapon's asset path."""
        return self._asset_path

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
        """:class: `Translator` Returns the weapon's shop category text."""
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


class Skin(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __repr__(self) -> str:
        return f"<Skin name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def _update(self, data: Any) -> None:
        self._uuid = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._theme_uuid: str = data['themeUuid']
        self._content_tier_uuid: str = data['contentTierUuid']
        self._display_icon: str = data['displayIcon']
        self._wallpaper: Optional[str] = data.get('wallpaper')
        self._asset_path: str = data['assetPath']
        self._chromas: List[Dict[str, Any]] = data['chromas']
        self._levels: List[Dict[str, Any]] = data['levels']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the skin's names."""
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
    def icon(self) -> Asset:
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
    def asset_path(self) -> str:
        """:class: `str` Returns the skin's asset path."""
        return self._asset_path

    @property
    def chromas(self) -> List[SkinChroma]:
        """:class: `list` Returns the skin's chromas."""
        return [SkinChroma(client=self._client, data=data) for data in self._chromas]

    @property
    def levels(self) -> List[SkinLevel]:
        """:class: `list` Returns the skin's levels."""
        return [SkinLevel(client=self._client, data=data) for data in self._levels]


class SkinChroma(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<SkinChroma name={self.name!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: str = data['displayIcon']
        self._full_render: str = data['fullRender']
        self._swatch: Optional[str] = data.get('swatch')
        self._streamed_video: Optional[str] = data.get('streamedVideo')
        self._asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def icon(self) -> Asset:
        """:class: `str` Returns the skin's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def icon_full_render(self) -> Asset:
        """:class: `str` Returns the skin's icon full render."""
        return Asset._from_url(client=self._client, url=self._full_render)

    @property
    def swatch(self) -> Optional[Asset]:
        """:class: `str` Returns the skin's swatch."""
        return (
            Asset._from_url(client=self._client, url=self._swatch)
            if self._swatch
            else None
        )

    @property
    def video(self) -> Optional[Asset]:
        """:class: `str` Returns the skin's video."""
        return (
            Asset._from_url(client=self._client, url=self._streamed_video)
            if self._streamed_video
            else None
        )


class SkinLevel(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<SkinLevel name={self.name!r} level={self.level!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._level: Optional[str] = data.get('levelItem')
        self._display_icon: str = data['displayIcon']
        self._streamed_video: Optional[str] = data.get('streamedVideo')
        self._asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the skin's names."""
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
    def icon(self) -> Asset:
        """:class: `str` Returns the skin's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def video(self) -> Optional[Asset]:
        """:class: `str` Returns the skin's video."""
        return (
            Asset._from_url(client=self._client, url=self._streamed_video)
            if self._streamed_video
            else None
        )

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the skin's asset path."""
        return self._asset_path