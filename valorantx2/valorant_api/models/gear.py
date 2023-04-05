from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from ..asset import Asset
from ..enums import Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    from ..cache import CacheState
    from ..types.gear import Gear_ as GearPayload, GridPosition as GridPositionPayload, ShopData as ShopDataPayload

# fmt: off
__all__ = (
    'Gear',
)
# fmt: on


class ShopData:
    def __init__(self, *, state: CacheState, data: ShopDataPayload) -> None:
        self._state: CacheState = state
        self.cost: int = data['cost']
        self.category: str = data['category']
        self._category_text: Union[str, Dict[str, str]] = data['categoryText']
        self._grid_position: GridPositionPayload = data['gridPosition']
        self._can_be_trashed: bool = data.get('canBeTrashed', False)
        self._image: Optional[str] = data['image']
        self._new_image: Optional[str] = data['newImage']
        self._new_image_2: Optional[str] = data['newImage2']
        self.asset_path: str = data['assetPath']

    def __int__(self) -> int:
        return self.cost

    @property
    def category_text_localizations(self) -> Localization:
        """:class: `Localization` Returns the gear's shop category text."""
        return Localization(self._category_text, locale=self._state.locale)

    @property
    def category_text(self) -> str:
        """:class: `str` Returns the gear's shop category text."""
        return self.category_text_localizations.american_english

    @property
    def image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the gear's image."""
        if self._image is None:
            return None
        return Asset._from_url(state=self._state, url=self._image)

    @property
    def new_image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the gear's new image."""
        if self._new_image is None:
            return None
        return Asset._from_url(state=self._state, url=self._new_image)

    @property
    def new_image_2(self) -> Optional[Asset]:
        """:class: `Asset` Returns the gear's new image."""
        if self._new_image_2 is None:
            return None
        return Asset._from_url(state=self._state, url=self._new_image_2)

    def can_be_trashed(self) -> bool:
        """:class: `bool` Returns whether the gear can be trashed."""
        return self._can_be_trashed


class Gear(BaseModel):
    def __init__(self, state: CacheState, data: GearPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._display_icon: str = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self._shop_data: ShopData = ShopData(state=self._state, data=data['shopData'])
        self._display_name_localized = Localization(self._display_name, locale=self._state.locale)
        self._description_localized = Localization(self._description, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Gear display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    def description_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._description_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the gear's name."""
        return self._display_name_localized

    @property
    def description(self) -> Localization:
        """:class: `str` Returns the gear's description."""
        return self._description_localized

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the gear's display icon."""
        return Asset._from_url(state=self._state, url=self._display_icon)

    @property
    def shop_data(self) -> ShopData:
        """:class: `ShopData` Returns the gear's shop data."""
        return self._shop_data

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the gear with the given UUID."""
    #     data = client._assets.get_gear(uuid=uuid)
    #     return cls(client=client, data=data) if data else None
