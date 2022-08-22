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

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ..asset import Asset
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'PlayerCard',
)
# fmt: on


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
        self.is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._display_icon: Optional[str] = data['displayIcon']
        self._small_icon: Optional[str] = data['smallArt']
        self._wide_icon: Optional[str] = data['wideArt']
        self._large_icon: Optional[str] = data['largeArt']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self.asset_path: str = data['assetPath']
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
    def display_icon(self) -> Optional[Asset]:
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
    # def is_owned(self) -> bool:  # TODO: Someday...
    #     """:class: `bool` Returns whether the player card is owned."""
    #     return self._client.player_cards.is_owned(self.uuid)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        data = client.assets.get_player_card(uuid)
        return cls(client=client, data=data) if data else None
