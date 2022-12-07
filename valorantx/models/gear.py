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

from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional

from ..asset import Asset
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'Gear',
)
# fmt: on


class Gear(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Dict[str, str] = data['displayName']
        self._description: Dict[str, str] = data['description']
        self._display_icon: str = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self._shop: Dict[str, Any] = data['shopData']
        self.cost: int = self._shop['cost']
        self.shop_category: str = self._shop['category']
        self._shop_category_text: Dict[str, str] = self._shop['categoryText']
        self.shop_grid_position: Optional[Dict[str, int]] = self._shop['gridPosition']
        self._can_be_trashed: bool = self._shop.get('canBeTrashed', False)
        self._image: Optional[str] = self._shop['image']
        self._new_image: Optional[str] = self._shop['newImage']
        self._new_image_2: Optional[str] = self._shop['newImage2']
        self.shop_asset_path: str = self._shop['assetPath']

    def __str__(self) -> str:
        return self.display_name

    def __int__(self) -> int:
        return self.cost

    def __repr__(self) -> str:
        return f'<Gear display_name={self.display_name!r}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the gear's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the gear's name."""
        return self.name_localizations.american_english

    @property
    def description_localizations(self) -> Localization:
        """:class: `Localization` Returns the gear's descriptions."""
        return Localization(self._description, locale=self._client.locale)

    @property
    def description(self) -> str:
        """:class: `str` Returns the gear's description."""
        return self.description_localizations.american_english

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the gear's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def shop_category_text_localizations(self) -> Localization:
        """:class: `Localization` Returns the gear's shop category text."""
        return Localization(self._shop_category_text, locale=self._client.locale)

    @property
    def shop_category_text(self) -> str:
        """:class: `str` Returns the gear's shop category text."""
        return self.shop_category_text_localizations.american_english

    @property
    def image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the gear's image."""
        if self._image is None:
            return None
        return Asset._from_url(client=self._client, url=self._image)

    @property
    def new_image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the gear's new image."""
        if self._new_image is None:
            return None
        return Asset._from_url(client=self._client, url=self._new_image)

    @property
    def new_image_2(self) -> Optional[Asset]:
        """:class: `Asset` Returns the gear's new image."""
        if self._new_image_2 is None:
            return None
        return Asset._from_url(client=self._client, url=self._new_image_2)

    def can_be_trashed(self) -> bool:
        """:class: `bool` Returns whether the gear can be trashed."""
        return self._can_be_trashed

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the gear with the given UUID."""
        data = client._assets.get_gear(uuid=uuid)
        return cls(client=client, data=data) if data else None
