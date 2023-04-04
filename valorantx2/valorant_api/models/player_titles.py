from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Union

from ..enums import Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..cache import CacheState

    # from ..client import Client

# fmt: off
__all__ = (
    'PlayerTitle',
)
# fmt: on


class PlayerTitle(BaseModel):
    def __init__(self, *, state: CacheState, data: Mapping[str, Any]) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Dict[str, str] = data['displayName']
        self._title_text: Dict[str, str] = data['titleText']
        self._is_hidden_if_not_owned: bool = data.get('isHiddenIfNotOwned', False)
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)
        self._title_text_localized: Localization = Localization(self._title_text, locale=self._state.locale)

    def __str__(self) -> str:
        return self.text.locale

    def __repr__(self) -> str:
        return f"<PlayerTitle display_name={self.display_name!r} text={self.text!r}>"

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    def title_text_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._title_text_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the player title's name."""
        return self._display_name_localized

    @property
    def text(self) -> Localization:
        """:class: `str` Returns the player title's title text."""
        return self._title_text_localized

    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the player title is hidden if not owned."""
        return self._is_hidden_if_not_owned

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the player title with the given UUID."""
    #     data = client._assets.get_player_title(uuid=uuid)
    #     return cls(client=client, data=data) if data else None
