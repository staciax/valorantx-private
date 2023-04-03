from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from ...enums import Locale
from ..asset import Asset
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    from ..cache import CacheState
    from ..types.bundles import Bundle as BundlePayload

    # from .buddy import Buddy
    # from .player_card import PlayerCard
    # from .spray import Spray
    # from .weapons import Skin

# fmt: off
__all__ = (
    'Bundle',
)
# fmt: on


class Bundle(BaseModel):
    def __init__(self, *, state: CacheState, data: BundlePayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_name_sub_text: Union[str, Dict[str, str]] = data['displayNameSubText']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._description_extra: Union[str, Dict[str, str]] = data['extraDescription']
        self._description_promo: Union[str, Dict[str, str]] = data['extraDescription']
        self._display_icon: str = data['displayIcon']
        self._display_icon_2: str = data['displayIcon2']
        self._vertical_promo_image: str = data['verticalPromoImage']
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)
        self._display_name_sub_text_localized: Localization = Localization(
            self._display_name_sub_text, locale=self._state.locale
        )
        self._description_localized: Localization = Localization(self._description, locale=self._state.locale)
        self._description_extra_localized: Localization = Localization(self._description_extra, locale=self._state.locale)
        self._description_promo_localized: Localization = Localization(self._description_promo, locale=self._state.locale)
        # self._items: List[Union[Skin, Buddy, Spray, PlayerCard]] = []

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Bundle display_name={self.display_name!r}>'

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
        return Asset._from_url(state=self._state, url=self._display_icon)

    @property
    def display_icon_2(self) -> Asset:
        """:class: `Asset` Returns the bundle's icon 2."""
        return Asset._from_url(state=self._state, url=self._display_icon_2)

    @property
    def vertical_promo_image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the bundle's vertical promo image."""
        if self._vertical_promo_image is None:
            return None
        return Asset._from_url(state=self._state, url=self._vertical_promo_image)

    # def add_item(self, item: Union[Skin, Buddy, Spray, PlayerCard]) -> None:
    #     # avoid circular imports
    #     from .buddy import Buddy
    #     from .player_card import PlayerCard
    #     from .spray import Spray
    #     from .weapons import Skin

    # self._items.append(item)

    # @property
    # def items(self) -> List[Union[Skin, Buddy, Spray, PlayerCard]]:
    #     """:class: `List[Union[Buddy, Spray, PlayerCard]]` Returns the bundle's items."""
    #     return self._items
