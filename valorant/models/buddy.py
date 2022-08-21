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
    from typing_extensions import Self
    from ..client import Client

__all__ = (
    'Buddy',
    'BuddyLevel'
)

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
        self.is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self._levels: List[Dict[str, Any]] = data['levels']
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
    def theme(self) -> str:  # TODO: Theme Object
        """:class: `str` Returns the buddy's theme."""
        return self._theme_uuid

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the buddy's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def levels(self) -> List[BuddyLevel]:
        """:class: `List[BuddyLevel]` Returns the buddy's levels."""
        return [BuddyLevel(client=self._client, data=level) for level in self._levels]

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

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the buddy with the given UUID."""
        data = client.assets.get_buddy(uuid)
        return cls(client=client, data=data) if data else None

class BuddyLevel(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<BuddyLevel name={self.name!r} base={self.base_buddy!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._base_buddy_uuid: Optional[str] = data['base_uuid']
        self.level: int = data['charmLevel']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']
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
    def display_icon(self) -> Optional[Asset]:
        """:class: `str` Returns the buddy's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon) if self._display_icon else None

    @property
    def price(self) -> int:
        """:class: `int` Returns the buddy's price."""
        return self._price

    @property
    def base_buddy(self) -> Buddy:
        """:class: `Buddy` Returns the base buddy."""
        return self._client.get_buddy(self._base_buddy_uuid)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the buddy level with the given UUID."""
        data = client.assets.get_buddy_level(uuid)
        return cls(client=client, data=data) if data else None
