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

from .base import BaseModel

from ..localization import Localization

from typing import Any, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from ..client import Client

# fmt: off
__all__ = (
    'PlayerTitle',
)
# fmt: on

class PlayerTitle(BaseModel):

    def __init__(self, *, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"<PlayerTitle name={self.name!r} text={self.text!r}>"

    def _update(self, data: Any) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._title_text: Union[str, Dict[str, str]] = data['titleText']
        self.is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self.asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the player title's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the player title's name."""
        return self.name_localizations.american_english

    @property
    def text_localizations(self) -> Localization:
        """:class: `Translator` Returns the player title's title text."""
        return Localization(self._title_text, locale=self._client.locale)

    @property
    def text(self) -> str:
        """:class: `str` Returns the player title's title text."""
        return self.text_localizations.american_english

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the player title with the given UUID."""
        data = client.assets.get_player_title(uuid)
        return cls(client=client, data=data) if data else None
