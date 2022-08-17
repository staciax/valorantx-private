from __future__ import annotations

from .base import BaseObject

from ..asset_manager import Asset
from ..localization import Localization
from ..enums import ItemType

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client
    from . import (
        # Skin,
        Buddy,
        Spray,
        PlayerCard
    )

__all__ = ('Bundle',)

class Bundle(BaseObject):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def _update(self, data: Optional[Any]) -> None:
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_name_sub_text: Union[str, Dict[str, str]] = data['displayNameSubText']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._description_extra: Union[str, Dict[str, str]] = data['extraDescription']
        self._description_promo: Union[str, Dict[str, str]] = data['extraDescription']
        self._display_icon: str = data['displayIcon']
        self._display_icon_2: str = data['displayIcon2']
        self._vertical_promo_image: str = data['verticalPromoImage']
        self._asset_path: str = data['assetPath']
        self._price: int = 0
        self._discount_price: int = 0

        if self._extras.get('bundle') is None:
            self._items: List[Union[Buddy, Spray, PlayerCard]] = data.get('items', [])
        else:
            self._bundle: Any = self._extras['bundle']
            self._duration: int = self._bundle['DurationRemainingInSeconds']
            self._whole_sale_only: bool = self._bundle['WholesaleOnly']
            self._items: List[Union[Buddy, Spray, PlayerCard]] = []  # Skin
            self.__bundle_items(self._bundle['Items'])

    def __repr__(self) -> str:
        return f'<Bundle uuid={self.uuid!r} name={self.name!r}>'

    def __str__(self) -> str:
        return self.name

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
    def icon(self) -> Asset:
        """:class: `Asset` Returns the bundle's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def icon_2(self) -> Asset:
        """:class: `Asset` Returns the bundle's icon 2."""
        return Asset._from_url(client=self._client, url=self._display_icon_2)

    @property
    def vertical_promo_image(self) -> Asset:
        """:class: `Asset` Returns the bundle's vertical promo image."""
        return Asset._from_url(client=self._client, url=self._vertical_promo_image)

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the bundle's asset path."""
        return self._asset_path

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
