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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Mapping

from ..asset import Asset
from ..localization import Localization
from .base import BaseFeaturedBundleItem, BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from .theme import Theme

__all__ = ('Buddy', 'BuddyLevel', 'BuddyBundle')


class Buddy(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self._levels: List[Dict[str, Any]] = data['levels']
        self._price: int = 0

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<Buddy display_name={self.display_name!r}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the buddy's name."""
        return self.name_localizations.american_english

    @property
    def theme(self) -> Theme:
        """:class: `Theme` Returns the buddy's theme."""
        return self._client.get_theme(uuid=self._theme_uuid)

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the buddy's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def levels(self) -> List[BuddyLevel]:
        """:class: `List[BuddyLevel]` Returns the buddy's levels."""
        return [BuddyLevel(client=self._client, data=level) for level in self._levels]

    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the buddy is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @property
    def price(self) -> int:
        """:class: `int` Returns the buddy's price."""
        if self._price == 0:
            if len(self.levels) > 0:
                self._price = self.levels[0].price
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the buddy with the given UUID."""
        data = client.assets.get_buddy(uuid)
        return cls(client=client, data=data) if data else None


class BuddyLevel(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._base_buddy_uuid: Optional[str] = data['base_uuid']
        self.level: int = data['charmLevel']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self._price: int = self._client.get_item_price(self.uuid)

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<BuddyLevel display_name={self.display_name!r} base={self.base_buddy!r}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
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

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    @property
    def base_buddy(self) -> Buddy:
        """:class: `Buddy` Returns the base buddy."""
        return self._client.get_buddy(self._base_buddy_uuid)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the buddy level with the given UUID."""
        data = client.assets.get_buddy_level(uuid)
        return cls(client=client, data=data) if data else None


class BuddyBundle(BuddyLevel, BaseFeaturedBundleItem):
    def __init__(self, client: Client, data: Optional[Mapping[str, Any]], bundle: Dict[str, Any]) -> None:
        BuddyLevel.__init__(self, client=client, data=data)
        BaseFeaturedBundleItem.__init__(self, bundle=bundle)

    def __repr__(self) -> str:
        attrs = [('display_name', self.display_name), ('price', self.price), ('discounted_price', self.discounted_price)]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @classmethod
    def _from_bundle(cls, client: Client, uuid: str, bundle: Dict[str, Any]) -> Optional[Self]:
        """Returns the buddy level with the given UUID."""
        data = client.assets.get_buddy_level(uuid)
        return cls(client=client, data=data, bundle=bundle) if data else None
