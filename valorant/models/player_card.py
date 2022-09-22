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
from .base import BaseFeaturedBundleItem, BaseModel
from .theme import Theme

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'PlayerCard',
    'PlayerCardBundle'
)
# fmt: on


class PlayerCard(BaseModel):
    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data.get('isHiddenIfNotOwned', False)
        self._display_icon: Optional[str] = data['displayIcon']
        self._small_icon: Optional[str] = data['smallArt']
        self._wide_icon: Optional[str] = data['wideArt']
        self._large_icon: Optional[str] = data['largeArt']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self.asset_path: str = data['assetPath']
        self._price = self._client.get_item_price(self.uuid)

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<PlayerCard display_name={self.display_name!r}>"

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
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
    def theme(self) -> Optional[Theme]:
        """:class: `Theme` Returns the buddy's theme."""
        return Theme._from_uuid(client=self._client, uuid=self._theme_uuid)

    @property
    def price(self) -> int:
        """:class: `int` Returns the buddy's price."""
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the buddy is hidden if not owned."""
        return self._is_hidden_if_not_owned

    # @property
    # def is_owned(self) -> bool:  # TODO: Someday...
    #     """:class: `bool` Returns whether the player card is owned."""
    #     return self._client.player_cards.is_owned(self.uuid)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        data = client.assets.get_player_card(uuid)
        return cls(client=client, data=data) if data else None


class PlayerCardBundle(PlayerCard, BaseFeaturedBundleItem):
    def __init__(self, client: Client, data: Optional[Dict[str, Any]], bundle: Dict[str, Any]) -> None:
        PlayerCard.__init__(self, client=client, data=data)
        BaseFeaturedBundleItem.__init__(self, bundle=bundle)

    def __repr__(self) -> str:
        attrs = [('display_name', self.display_name), ('price', self.price), ('discounted_price', self.discounted_price)]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @classmethod
    def _from_bundle(cls, client: Client, uuid: str, bundle: Dict[str, Any]) -> Optional[Self]:
        """Returns the spray level with the given UUID."""
        data = client.assets.get_player_card(uuid)
        return cls(client=client, data=data, bundle=bundle) if data else None
