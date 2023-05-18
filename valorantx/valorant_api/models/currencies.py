from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from ..asset import Asset
from ..enums import Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..cache import CacheState
    from ..types.currencies import Currency as CurrencyPayload

# fmt: off
__all__ = (
    'Currency',
)
# fmt: on


class Currency(BaseModel):
    def __init__(self, state: CacheState, data: CurrencyPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_name_singular: Union[str, Dict[str, str]] = data['displayNameSingular']
        self._display_icon: Optional[str] = data['displayIcon']
        self._large_icon: Optional[str] = data['largeIcon']
        self.asset_path: str = data['assetPath']
        # self._value: int = 0
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)
        self._display_name_singular_localized: Localization = Localization(
            self._display_name_singular, locale=self._state.locale
        )

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Currency display_name={self.display_name!r}>'

    # def __int__(self) -> int:
    #     return self.value

    # def __lt__(self, other: object) -> bool:
    #     return isinstance(other, Currency) and self.value < other.value

    # def __le__(self, other: object) -> bool:
    #     return isinstance(other, Currency) and self.value <= other.value

    # def __eq__(self, other: object) -> bool:
    #     return isinstance(other, Currency) and self.value == other.value

    # def __ne__(self, other: object) -> bool:
    #     return not self.__eq__(other)

    # def __gt__(self, other: object) -> bool:
    #     return isinstance(other, Currency) and self.value > other.value

    # def __ge__(self, other: object) -> bool:
    #     return isinstance(other, Currency) and self.value >= other.value

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    def display_name_singular_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_singular_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the agent's name."""
        return self._display_name_localized

    @property
    def display_name_singular(self) -> Localization:
        """:class: `str` Returns the agent's singular name."""
        return self._display_name_singular_localized

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Optional[Asset]` Returns the agent's icon."""
        if self._display_icon is None:
            return None
        return Asset._from_url(state=self._state, url=self._display_icon)

    @property
    def large_icon(self) -> Optional[Asset]:
        """:class: `Optional[Asset]` Returns the agent's large icon."""
        if self._large_icon is None:
            return None
        return Asset._from_url(state=self._state, url=self._large_icon)

    # @property
    # def value(self) -> int:
    #     """:class: `int` Returns the agent's value."""
    #     return self._value

    # @value.setter
    # def value(self, value: int) -> None:
    #     self._value = value

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the currency with the given UUID."""
    #     data = client._assets.get_currency(uuid)
    #     return cls(client=client, data=data) if data else None
