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
from ..enums import ItemType


from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client
    from typing_extensions import Self
    from .weapons import Skin
    from .player_card import PlayerCard
    from .spray import Spray
    from .buddy import Buddy

# fmt: off
__all__ = (
    'Bundle',
)
# fmt: on

class Bundle(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]], **kwargs) -> None:
        super().__init__(client=client, data=data, **kwargs)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Bundle name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_name_sub_text: Union[str, Dict[str, str]] = data['displayNameSubText']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._description_extra: Union[str, Dict[str, str]] = data['extraDescription']
        self._description_promo: Union[str, Dict[str, str]] = data['extraDescription']
        self._display_icon: str = data['displayIcon']
        self._display_icon_2: str = data['displayIcon2']
        self._vertical_promo_image: str = data['verticalPromoImage']
        self.asset_path: str = data['assetPath']
        self._price: int = 0
        self._discount_price: int = 0
        self._items: List[Union[Skin, Buddy, Spray, PlayerCard]] = []

        if self._extras.get('bundle') is None:  # TODO: futured_bundle
            self._items = data.get('items', [])
            # TODO: filter items
        else:
            self._bundle: Any = self._extras['bundle']
            self._duration: int = self._bundle['DurationRemainingInSeconds']
            self._whole_sale_only: bool = self._bundle['WholesaleOnly']
            self.__bundle_items(self._bundle['Items'])

    def __bundle_items(
            self,
            items: List[Dict[str, Any]]
    ) -> None:

        for item in items:
            item_type = item['Item']['ItemTypeID']
            item_uuid = item['Item']['ItemID']
            is_promo_item = item['IsPromoItem']
            self._price += item['BasePrice']
            self._discount_price += item['DiscountedPrice']

            # if item_type == ItemType.Skin.value:
            #     self.e_items.append(
            #         Skin._from_uuid(client=self._client, uuid=item_uuid, bundle=item)
            #     )
            # if item_type == ItemType.Spray.value:
            #     self.e_items.append(
            #         Spray._from_uuid(client=self._client, uuid=item_uuid, bundle=item)
            #     )
            # elif item_type == ItemType.Buddy.value:
            #     self.e_items.append(
            #         Buddy._from_uuid(client=self._client, uuid=item_uuid, bundle=item)
            #     )
            # elif item_type == ItemType.PlayerCard.value:
            #     self.e_items.append(
            #         PlayerCard._from_uuid(client=self._client, uuid=item_uuid, bundle=item)
            #     )

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the bundle's name localizations."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the bundle's name."""
        return self.name_localizations.american_english

    @property
    def name_sub_localizations(self) -> Localization:
        """:class: `Localization` Returns the bundle's sub name localizations."""
        return Localization(self._display_name_sub_text, locale=self._client.locale)

    @property
    def sub_name(self) -> str:
        """:class: `str` Returns the bundle's sub name."""
        return self.name_sub_localizations.american_english

    @property
    def description_localizations(self) -> Localization:
        """:class: `Localization` Returns the bundle's description localizations."""
        return Localization(self._description, locale=self._client.locale)

    @property
    def description(self) -> str:
        """:class: `str` Returns the bundle's description."""
        return self.description_localizations.american_english

    @property
    def description_extra_localizations(self) -> Localization:
        """:class: `Localization` Returns the bundle's description extra localizations."""
        return Localization(self._description_extra, locale=self._client.locale)

    @property
    def description_extra(self) -> str:
        """:class: `str` Returns the bundle's description extra localizations."""
        return self.description_extra_localizations.american_english

    @property
    def description_promo_localizations(self) -> Localization:
        """:class: `Localization` Returns the bundle's description promo localizations."""
        return Localization(self._description_promo, locale=self._client.locale)

    @property
    def description_promo(self) -> str:
        """:class: `str` Returns the bundle's description promo."""
        return self.description_promo_localizations.american_english

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the bundle's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def display_icon_2(self) -> Asset:
        """:class: `Asset` Returns the bundle's icon 2."""
        return Asset._from_url(client=self._client, url=self._display_icon_2)

    @property
    def vertical_promo_image(self) -> Asset:
        """:class: `Asset` Returns the bundle's vertical promo image."""
        return Asset._from_url(client=self._client, url=self._vertical_promo_image)

    @property
    def items(self) -> List[Union[Buddy, Spray, PlayerCard]]:
        """:class: `List[Union[Buddy, Spray, PlayerCard]]` Returns the bundle's items."""
        return self._items

    # bundle properties

    @property
    def duration(self) -> int:
        """:class: `int` Returns the bundle's duration."""
        return self._duration

    @property
    def whole_sale_only(self) -> bool:
        """:class: `bool` Returns the bundle's wholesale only."""
        return self._whole_sale_only

    @property
    def price(self) -> int:
        """:class: `int` Returns the bundle's price."""
        return self._price

    @property
    def discount_price(self) -> int:
        """:class: `int` Returns the bundle's discount price."""
        return self._discount_price

    @classmethod
    def _from_store(cls, client: Client, bundle: Dict[str, Any]) -> Self:
        """Creates a bundle from a store response."""
        uuid = bundle['DataAssetID']
        data = client.assets.get_bundle(uuid)
        return cls(client=client, data=data, bundle=bundle)
