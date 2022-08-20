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
from ..localization import Localization

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

__all__ = (
    'Spray',
    'SprayLevel'
)

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
        self._category: str = data['category']
        self._theme_uuid: str = data['themeUuid']
        self._display_icon: Optional[str] = data['displayIcon']
        self._full_icon: Optional[str] = data.get('fullIcon')
        self._full_transparent_icon: Optional[str] = data.get('fullTransparentIcon')
        self._animation_png: Optional[str] = data.get('animationPng')
        self._animation_gif: Optional[str] = data.get('animationGif')
        self._asset_path: str = data['assetPath']
        self._levels: List[Dict[str, Any]] = data['levels']
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
    def display_icon(self) -> Optional[Asset]:
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
    def asset_path(self) -> str:
        """:class: `str` Returns the skin's asset path."""
        return self._asset_path

    @property
    def levels(self) -> List[SprayLevel]:
        """:class: `list` Returns the skin's levels."""
        return [SprayLevel(client=self._client, data=level) for level in self._levels]

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

class SprayLevel(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<SprayLevel name={self.name!r} default={self.default!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._default_uuid: Optional[str] = data.get('default_uuid')
        self._spray_level: int = data['sprayLevel']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data.get('displayIcon')
        self._asset_path: str = data['assetPath']
        self._price: int = data.get('price', 0)

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the buddy's name."""
        return self.name_localizations.american_english

    @property
    def level(self) -> int:
        """:class: `int` Returns the spray level."""
        return self._spray_level

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `str` Returns the spray's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon) if self._display_icon else None

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the asset path of the spray."""
        return self._asset_path

    @property
    def price(self) -> int:
        """:class: `int` Returns the price of the spray."""
        return self._price

    @property
    def default(self) -> Spray:
        """:class: `Spray` Returns the spray's default."""
        return self._client.assets.get_spray(self._default_uuid)
