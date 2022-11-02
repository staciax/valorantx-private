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

from ..asset import Asset
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'Currency',
)
# fmt: on


class Currency(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_name_singular: Union[str, Dict[str, str]] = data['displayNameSingular']
        self._display_icon: Optional[str] = data.get('displayIcon')
        self._large_icon: Optional[str] = data.get('largeIcon')
        self.asset_path: str = data['assetPath']

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<Currency display_name={self.display_name!r}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
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
    def display_icon(self) -> Optional[Asset]:
        """:class: `Optional[Asset]` Returns the agent's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon) if self._display_icon else None

    @property
    def large_icon(self) -> Optional[Asset]:
        """:class: `Optional[Asset]` Returns the agent's large icon."""
        return Asset._from_url(client=self._client, url=self._large_icon) if self._large_icon else None

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the currency with the given UUID."""
        data = client.assets.get_currency(uuid)
        return cls(client=client, data=data) if data else None
