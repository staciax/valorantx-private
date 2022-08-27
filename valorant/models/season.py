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

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from .. import utils
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    import datetime

    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'Season',
)
# fmt: on


class Season(BaseModel):
    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        attrs = [
            ('uuid', self.uuid),
            ('display_name', self.display_name),
            ('type', self.type),
            ('start_time', self.start_time),
            ('end_time', self.end_time),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self.type: str = data['type']
        self._start_time_iso: Union[str, datetime.datetime] = data['startTime']
        self._end_time_iso: Union[str, datetime.datetime] = data['endTime']
        self._parent_uuid: str = data['parentUuid']
        self.asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the season's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the season's name."""
        return self.name_localizations.american_english

    @property
    def start_time(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the season's start time."""
        return utils.parse_iso_datetime(self._start_time_iso)

    @property
    def end_time(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the season's end time."""
        return utils.parse_iso_datetime(self._end_time_iso)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the season with the given UUID."""
        data = client.assets.get_season(uuid)
        return cls(client=client, data=data) if data else None
