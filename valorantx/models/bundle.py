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

import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Union

from ..asset import Asset
from ..enums import ItemType, Locale
from ..localization import Localization
from .base import BaseModel
from .buddy import BuddyBundle
from .player_card import PlayerCardBundle
from .spray import SprayBundle
from .weapons import SkinBundle

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from .buddy import Buddy
    from .player_card import PlayerCard
    from .spray import Spray
    from .weapons import Skin

# fmt: off
__all__ = (
    'Bundle',
    'FeaturedBundle',
)
# fmt: on


class Bundle(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any], *, is_featured_bundle: bool = False) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Dict[str, str] = data['displayName']
        self._display_name_sub_text: Dict[str, str] = data['displayNameSubText']
        self._description: Dict[str, str] = data['description']
        self._description_extra: Dict[str, str] = data['extraDescription']
        self._description_promo: Dict[str, str] = data['extraDescription']
        self._display_icon: str = data['displayIcon']
        self._display_icon_2: str = data['displayIcon2']
        self._vertical_promo_image: str = data['verticalPromoImage']
        self.asset_path: str = data['assetPath']
        self._price: int = 0
        self._discount_price: int = 0
        self._items: List[Union[Skin, Buddy, Spray, PlayerCard]] = []
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._client.locale)
        self._display_name_sub_text_localized: Localization = Localization(
            self._display_name_sub_text, locale=self._client.locale
        )
        self._description_localized: Localization = Localization(self._description, locale=self._client.locale)
        self._description_extra_localized: Localization = Localization(self._description_extra, locale=self._client.locale)
        self._description_promo_localized: Localization = Localization(self._description_promo, locale=self._client.locale)

        if not is_featured_bundle:
            if data.get('Items') is not None:
                self._bundle_items(data['Items'])

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Bundle display_name={self.display_name!r}>'

    def _bundle_items(self, items: List[Dict[str, Any]]) -> None:
        for item in items:
            item_type = item['Item']['ItemTypeID']
            item_uuid = item['Item']['ItemID']

            self._price += item.get('BasePrice', 0)
            self._discount_price += item.get('DiscountedPrice', 0)

            if item_type == ItemType.skin_level.value:
                self._items.append(SkinBundle._from_bundle(client=self._client, uuid=item_uuid, bundle=item))  # type: ignore
            elif item_type == ItemType.spray.value:
                self._items.append(SprayBundle._from_bundle(client=self._client, uuid=item_uuid, bundle=item))  # type: ignore
            elif item_type == ItemType.buddy_level.value:
                self._items.append(BuddyBundle._from_bundle(client=self._client, uuid=item_uuid, bundle=item))  # type: ignore
            elif item_type == ItemType.player_card.value:
                self._items.append(PlayerCardBundle._from_bundle(client=self._client, uuid=item_uuid, bundle=item))  # type: ignore

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    def display_name_sub_text_localized(self, locale: Optional[Union[Locale, str]] = None) -> Optional[str]:
        return self._display_name_sub_text_localized.from_locale(locale) if self._description is not None else None

    def description_localized(self, locale: Optional[Union[Locale, str]] = None) -> Optional[str]:
        return self._description_localized.from_locale(locale) if self._description is not None else None

    def description_extra_localized(self, locale: Optional[Union[Locale, str]] = None) -> Optional[str]:
        return self._description_extra_localized.from_locale(locale) if self._description_extra is not None else None

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the bundle's name."""
        return self._display_name_localized

    @property
    def display_sub_name(self) -> Optional[Localization]:
        """:class: `str` Returns the bundle's sub name."""
        return self._display_name_sub_text_localized if self._display_name_sub_text is not None else None

    @property
    def description(self) -> Optional[Localization]:
        """:class: `str` Returns the bundle's description."""
        return self._description_localized if self._description is not None else None

    @property
    def description_extra(self) -> Optional[Localization]:
        """:class: `str` Returns the bundle's description extra localizations."""
        return self._description_extra_localized if self._description_extra is not None else None

    @property
    def description_promo(self) -> Optional[Localization]:
        """:class: `str` Returns the bundle's description promo."""
        return self._description_promo_localized if self._description_promo is not None else None

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the bundle's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def display_icon_2(self) -> Asset:
        """:class: `Asset` Returns the bundle's icon 2."""
        return Asset._from_url(client=self._client, url=self._display_icon_2)

    @property
    def vertical_promo_image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the bundle's vertical promo image."""
        return (
            Asset._from_url(client=self._client, url=self._vertical_promo_image) if self._vertical_promo_image else None
        )  # noqa: E501

    @property
    def items(self) -> List[Union[Skin, Buddy, Spray, PlayerCard]]:
        """:class: `List[Union[Buddy, Spray, PlayerCard]]` Returns the bundle's items."""
        return self._items

    @property
    def price(self) -> int:
        """:class: `int` Returns the bundle's price."""
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the bundle with the given uuid."""
        data = client._assets.get_bundle(uuid)
        return cls(client=client, data=data) if data else None


class FeaturedBundle(Bundle):
    def __init__(self, client: Client, data: Mapping[str, Any], bundle: Dict[str, Any]) -> None:
        super().__init__(client, data, is_featured_bundle=True)
        self._items: List[Union[SkinBundle, SprayBundle, BuddyBundle, PlayerCardBundle]] = []
        self.duration: int = bundle.get('DurationRemainingInSeconds', 0)
        self._whole_sale_only: bool = bundle.get('WholesaleOnly', False)
        self._bundle_items(bundle['Items'])

    @property
    def items(self) -> List[Union[SkinBundle, SprayBundle, BuddyBundle, PlayerCardBundle]]:
        """:class: `List[Union[SkinBundle, SprayBundle, BuddyBundle, PlayerCardBundle]]` Returns the bundle's items."""
        return self._items

    def whole_sale_only(self) -> bool:
        """:class: `bool` Returns the bundle's wholesale only."""
        return self._whole_sale_only

    @property
    def expires_at(self) -> datetime.datetime:
        """:class: `datetime` Returns the bundle's expiration date."""
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=self.duration)

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
        data = client._assets.get_bundle(uuid)
        if data is None:
            raise ValueError(f'Bundle with uuid {uuid} not found.')
        return cls(client=client, data=data, bundle=bundle)
