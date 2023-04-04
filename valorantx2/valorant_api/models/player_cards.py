from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from ..asset import Asset
from ..enums import ItemType, Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..cache import CacheState
    from ..types.player_cards import PlayerCard as PlayerCardPayload

    # from .theme import Theme

# fmt: off
__all__ = (
    'PlayerCard',
)
# fmt: on


class PlayerCard(BaseModel):
    def __init__(self, *, state: CacheState, data: PlayerCardPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data.get('isHiddenIfNotOwned', False)
        self._display_icon: Optional[str] = data['displayIcon']
        self._small_icon: Optional[str] = data['smallArt']
        self._wide_icon: Optional[str] = data['wideArt']
        self._large_icon: Optional[str] = data['largeArt']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self.asset_path: str = data['assetPath']
        # self._price = self._client.get_item_price(self.uuid)
        self._is_favorite: bool = False
        self.type: ItemType = ItemType.player_card
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f"<PlayerCard display_name={self.display_name!r}>"

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the player card's name."""
        return self._display_name_localized

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the player card's icon."""
        if self._display_icon is None:
            return None
        return Asset._from_url(state=self._state, url=self._display_icon)

    @property
    def small_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the player card's small icon."""
        if self._small_icon is None:
            return None
        return Asset._from_url(state=self._state, url=self._small_icon)

    @property
    def wide_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the player card's wide icon."""
        if self._wide_icon is None:
            return None
        return Asset._from_url(state=self._state, url=self._wide_icon)

    @property
    def large_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the player card's large icon."""
        if self._large_icon is None:
            return None
        return Asset._from_url(state=self._state, url=self._large_icon)

    # @property
    # def theme(self) -> Optional[Theme]:
    #     """:class: `Theme` Returns the player card's theme."""
    #     return self._client.get_theme(uuid=self._theme_uuid)

    # @property
    # def price(self) -> int:
    #     """:class: `int` Returns the player card's price."""
    #     return self._price

    # @price.setter
    # def price(self, value: int) -> None:
    #     self._price = value

    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the player card is hidden if not owned."""
        return self._is_hidden_if_not_owned

    # @property
    # def is_owned(self) -> bool:  # TODO: Someday...
    #     """:class: `bool` Returns whether the player card is owned."""
    #     return self._client.player_cards.is_owned(self.uuid)

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     data = client._assets.get_player_card(uuid=uuid)
    #     return cls(client=client, data=data) if data else None
