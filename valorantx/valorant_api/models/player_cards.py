from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from ..asset import Asset
from ..enums import ItemType, Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..cache import CacheState
    from ..types.player_cards import PlayerCard as PlayerCardPayload
    from .themes import Theme

# fmt: off
__all__ = (
    'PlayerCard',
)
# fmt: on


class PlayerCard(BaseModel):
    def __init__(self, *, state: CacheState, data: PlayerCardPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._data: PlayerCardPayload = data
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data.get('isHiddenIfNotOwned', False)
        self._theme_uuid: Optional[str] = data['themeUuid']
        self._display_icon: Optional[str] = data['displayIcon']
        self._small_art: Optional[str] = data['smallArt']
        self._wide_art: Optional[str] = data['wideArt']
        self._large_art: Optional[str] = data['largeArt']
        self.asset_path: str = data['assetPath']
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
    def small_art(self) -> Optional[Asset]:
        """:class: `Asset` Returns the player card's small art."""
        if self._small_art is None:
            return None
        return Asset._from_url(state=self._state, url=self._small_art)

    @property
    def wide_art(self) -> Optional[Asset]:
        """:class: `Asset` Returns the player card's wide art."""
        if self._wide_art is None:
            return None
        return Asset._from_url(state=self._state, url=self._wide_art)

    @property
    def large_art(self) -> Optional[Asset]:
        """:class: `Asset` Returns the player card's large art."""
        if self._large_art is None:
            return None
        return Asset._from_url(state=self._state, url=self._large_art)

    @property
    def theme(self) -> Optional[Theme]:
        """:class: `Theme` Returns the player card's theme."""
        return self._state.get_theme(uuid=self._theme_uuid)

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

    @classmethod
    def _copy(cls, player_card: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._state = player_card._state
        self._data = player_card._data.copy()
        self._display_name = player_card._display_name
        self._is_hidden_if_not_owned = player_card._is_hidden_if_not_owned
        self._theme_uuid = player_card._theme_uuid
        self._display_icon = player_card._display_icon
        self._small_art = player_card._small_art
        self._wide_art = player_card._wide_art
        self._large_art = player_card._large_art
        self.asset_path = player_card.asset_path
        self.type = player_card.type
        self._display_name_localized = player_card._display_name_localized
        return self
