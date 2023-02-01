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

from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Union

from ..enums import Locale
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'PlayerTitle',
)
# fmt: on


class PlayerTitle(BaseModel):
    def __init__(self, *, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Dict[str, str] = data['displayName']
        self._title_text: Dict[str, str] = data['titleText']
        self._is_hidden_if_not_owned: bool = data.get('isHiddenIfNotOwned', False)
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=client.locale)
        self._title_text_localized: Localization = Localization(self._title_text, locale=client.locale)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"<PlayerTitle display_name={self.display_name!r} text={self.text!r}>"

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    def title_text_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._title_text_localized.from_locale(locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the player title's name."""
        return self._display_name_localized.locale

    @property
    def text(self) -> str:
        """:class: `str` Returns the player title's title text."""
        return self._title_text_localized.locale

    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the player title is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the player title with the given UUID."""
        data = client._assets.get_player_title(uuid=uuid)
        return cls(client=client, data=data) if data else None
