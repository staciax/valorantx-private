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

import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .. import utils
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'Mission',
)
# fmt: on


class Mission(BaseModel):
    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f'<Mission name={self.title!r}>'

    def __int__(self) -> int:
        return self.xp

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Optional[Union[str, Dict[str, str]]] = data['displayName']
        self._title: Optional[Union[str, Dict[str, str]]] = data['title']
        self.type: Optional[str] = data['type']
        self.xp: int = data['xpGrant']
        self.progress_to_complete: int = data['progressToComplete']
        self._activation_date_iso: str = data['activationDate']
        self._expiration_date_iso: str = data['expirationDate']
        self.tags: Optional[List[str]] = data['tags']
        self.objectives: Optional[Dict[str, Any]] = data['objectives']
        self.asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the mission's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the mission's name."""
        return self.name_localizations.american_english

    @property
    def title_localizations(self) -> Localization:
        """:class: `Localization` Returns the mission's titles."""
        return Localization(self._title, locale=self._client.locale)

    @property
    def title(self) -> str:
        """:class: `str` Returns the mission's title."""
        return self.title_localizations.american_english

    @property
    def activation_date(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the mission's activation date."""
        return utils.parse_iso_datetime(self._activation_date_iso)

    @property
    def expiration_date(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the mission's expiration date."""
        return utils.parse_iso_datetime(self._expiration_date_iso)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the mission with the given UUID."""
        data = client.assets.get_mission(uuid)
        return cls(client=client, data=data) if data else None
