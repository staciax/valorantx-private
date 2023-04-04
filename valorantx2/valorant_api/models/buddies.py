from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Union

from ..asset import Asset
from ..enums import ItemType, Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    from ..cache import CacheState
    from ..types.buddies import Buddy as BuddyPayload, BuddyLevel as BuddyLevelPayload

    # from .theme import Theme

__all__ = ('Buddy', 'BuddyLevel')


class Buddy(BaseModel):
    def __init__(self, *, state: CacheState, data: BuddyPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self._levels: List[BuddyLevelPayload] = data['levels']
        self.type: ItemType = ItemType.buddy
        self._name_localized = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Buddy display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the buddy's name."""
        return self._name_localized

    # @property
    # def theme(self) -> Optional[Theme]:
    #     """:class: `Theme` Returns the buddy's theme."""
    #     # Avoid circular import
    #     return self._state.get_theme(uuid=self._theme_uuid)

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the buddy's icon."""
        return Asset._from_url(state=self._state, url=self._display_icon)

    @property
    def levels(self) -> List[BuddyLevel]:
        """:class: `List[BuddyLevel]` Returns the buddy's levels."""
        return [BuddyLevel(state=self._state, data=level) for level in self._levels]

    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the buddy is hidden if not owned."""
        return self._is_hidden_if_not_owned

    def get_buddy_level(self, level: int = 1) -> Optional[BuddyLevel]:
        """Returns the buddy level for the given level number."""
        return next((b for b in self.levels if b.charm_level == level), None)


class BuddyLevel(BaseModel):
    def __init__(self, *, state: CacheState, data: BuddyLevelPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self.charm_level: int = data['charmLevel']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self._buddy: Optional[Buddy] = None
        self.type: ItemType = ItemType.buddy_level
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<BuddyLevel display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def level(self) -> int:
        """:class: `int` alias for :attr: `BuddyLevel.charm_level`"""
        return self.charm_level

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the buddy's name."""
        return self._display_name_localized

    @property
    def display_icon(self) -> Asset:
        """:class: `str` Returns the buddy's display icon."""
        return Asset._from_url(state=self._state, url=self._display_icon)

    @property
    def buddy(self) -> Optional[Buddy]:
        """:class: `Buddy` Returns the base buddy."""
        return self._buddy

    @buddy.setter
    def buddy(self, buddy: Buddy) -> None:
        self._buddy = buddy
