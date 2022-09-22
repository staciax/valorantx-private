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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ..asset import Asset
from ..enums import SpraySlotID
from ..localization import Localization
from .base import BaseFeaturedBundleItem, BaseModel
from .theme import Theme

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from ..types.collection import SprayLoadout as SprayLoadoutPayload

__all__ = ('Spray', 'SprayLevel', 'SprayLoadout', 'SprayLevelLoadout', 'SprayBundle')


class Spray(BaseModel):
    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]], bundle: Any = None) -> None:
        super().__init__(client=client, data=data, bundle=bundle)
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._category: Optional[str] = data['category']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self._display_icon: Optional[str] = data['displayIcon']
        self._full_icon: Optional[str] = data['fullIcon']
        self._full_transparent_icon: Optional[str] = data['fullTransparentIcon']
        self._animation_png: Optional[str] = data['animationPng']
        self._animation_gif: Optional[str] = data['animationGif']
        self.asset_path: str = data['assetPath']
        self._levels: List[Dict[str, Any]] = data['levels']
        self._price: int = self._client.get_item_price(self.uuid)

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<Spray display_name={self.display_name!r}>"

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def category(self) -> Optional[str]:
        """:class: `str` Returns the skin's category."""
        return self._category.removeprefix('EAresSprayCategory::') if self._category else None

    @property
    def theme(self) -> Optional[Theme]:
        if self._theme_uuid is None:
            return None
        return Theme._from_uuid(self._client, self._theme_uuid)

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
    def levels(self) -> List[SprayLevel]:
        """:class: `list` Returns the skin's levels."""
        return [SprayLevel(client=self._client, data=level) for level in self._levels]

    @property
    def price(self) -> int:
        """:class: `int` Returns the skin's price."""
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the spray with the given uuid."""
        data = client.assets.get_spray(uuid=uuid)
        return cls(client=client, data=data) if data else None


class SprayLevel(BaseModel):
    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._base_spray_uuid: Optional[str] = data['base_uuid']
        self._spray_level: int = data['sprayLevel']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self._asset_path: str = data['assetPath']
        self._price: int = 0

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<SprayLevel display_name={self.display_name!r} base={self.base_spray!r}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
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
        if self._price == 0:
            if hasattr(self.base_spray, 'price'):
                self._price = self.base_spray.price
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        """Sets the price of the spray."""
        self._price = value

    @property
    def base_spray(self) -> Spray:
        """:class: `Spray` Returns the base spray."""
        return self._client.get_spray(self._base_spray_uuid)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the spray level with the given uuid."""
        data = client.assets.get_spray_level(uuid=uuid)
        return cls(client=client, data=data) if data else None


class SprayBundle(Spray, BaseFeaturedBundleItem):
    def __init__(self, client: Client, data: Optional[Dict[str, Any]], bundle: Dict[str, Any]) -> None:
        Spray.__init__(self, client=client, data=data)
        BaseFeaturedBundleItem.__init__(self, bundle=bundle)

    def __repr__(self) -> str:
        attrs = [('display_name', self.display_name), ('price', self.price), ('discounted_price', self.discounted_price)]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @classmethod
    def _from_bundle(cls, client: Client, uuid: str, bundle: Dict[str, Any]) -> Optional[Self]:
        """Returns the spray level with the given UUID."""
        data = client.assets.get_spray(uuid)
        return cls(client=client, data=data, bundle=bundle) if data else None


class SprayLoadout(Spray):
    def __init__(self, client: Client, data: Any, loadout: SprayLoadoutPayload) -> None:
        super().__init__(client=client, data=data)
        self._slot = SpraySlotID._from_id(loadout['EquipSlotID'])

    def __repr__(self) -> str:
        return f'<SprayLoadout display_name={self.display_name!r}>'

    @property
    def slot(self) -> int:
        """:class: `int` Returns the slot number."""
        return self._slot

    @classmethod
    def _from_loadout(cls, client: Client, uuid: str, loadout: SprayLoadoutPayload) -> Self:
        data = client.assets.get_spray(uuid)
        return cls(client=client, data=data, loadout=loadout)


class SprayLevelLoadout(SprayLevel):
    def __init__(self, client: Client, data: Any, loadout: SprayLoadoutPayload) -> None:
        super().__init__(client=client, data=data)
        self._slot = SpraySlotID._from_id(loadout['EquipSlotID'])

    def __repr__(self) -> str:
        return f'<SprayLevelLoadout display_name={self.display_name!r} base={self.base_spray!r}>'

    @property
    def slot(self) -> int:
        """:class: `int` Returns the slot number."""
        return self._slot

    @classmethod
    def _from_loadout(cls, client: Client, uuid: str, loadout: SprayLoadoutPayload) -> Self:
        data = client.assets.get_spray_level(uuid)
        return cls(client=client, data=data, loadout=loadout)
