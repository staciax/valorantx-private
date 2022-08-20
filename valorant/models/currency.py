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

from ..asset import Asset
from ..localization import Localization
from .base import BaseModel

from typing import Any, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

# fmt: off
__all__ = (
    'Currency',
)
# fmt: on

class Currency(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Currency name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_name_singular: Union[str, Dict[str, str]] = data['displayNameSingular']
        self._display_icon: str = data['displayIcon']
        self._large_icon: str = data['largeIcon']
        self.asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the agent's name."""
        return self.name_localizations.american_english

    @property
    def name_singular_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's singular names."""
        return Localization(self._display_name_singular, locale=self._client.locale)

    @property
    def name_singular(self) -> str:
        """:class: `str` Returns the agent's singular name."""
        return self.name_singular_localizations.american_english

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the agent's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def large_icon(self) -> Asset:
        """:class: `Asset` Returns the agent's large icon."""
        return Asset._from_url(client=self._client, url=self._large_icon)
