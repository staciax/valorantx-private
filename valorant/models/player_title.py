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

from typing import Optional, Dict, Any, Union

from .base import BaseModel
from ..localization import Localization

from typing import Optional, Dict, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

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
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._asset_path: str = data['assetPath']

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

    @property
    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the player title is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the player title's asset path."""
        return self._asset_path
