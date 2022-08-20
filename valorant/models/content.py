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

from .base import BaseModel

from .. import utils
from ..asset import Asset
from ..localization import Localization

from typing import Any, List, Optional, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

__all__ = (
    'Content',
    'ContentTier'
)

class Content:

    def __init__(self, client: Client, data: Any) -> None:
        self._client = client
        self._update(data)

    def __repr__(self) -> str:
        return f"<Content season={self.seasons!r}"

    def _update(self, data: Any) -> None:
        self._disabled_ids: List[str] = data['DisabledIDs']
        self._seasons: List[ContentSeason] = data['Seasons']
        self._events: List[str] = data['Events']

    @property
    def disabled_ids(self) -> List[str]:
        return self._disabled_ids

    @property
    def seasons(self) -> List[ContentSeason]:
        return [ContentSeason(season) for season in self._seasons]

    @property
    def events(self) -> List[ContentEvent]:
        return [ContentEvent(event) for event in self._events]

class ContentSeason:
    def __init__(self, data: Any) -> None:
        self._update(data)

    def __repr__(self) -> str:
        attrs = [
            ('id', self.id),
            ('name', self.name),
            ('type', self.type),
            ('is_active', self.is_active),
            ('start_time', self.start_time),
            ('end_time', self.end_time),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def _update(self, data: Any) -> None:
        self.id: str = data['ID']
        self.name: str = data['Name']
        self.type: str = data['Type']
        self.is_active: bool = data['IsActive']
        self._start_time: str = data['StartTime']
        self._end_time: str = data['EndTime']

    @property
    def start_time(self) -> datetime:
        return utils.parse_iso_datetime(self._start_time)

    @property
    def end_time(self) -> datetime:
        return utils.parse_iso_datetime(self._end_time)

class ContentEvent:
    def __init__(self, data: Any) -> None:
        self._update(data)

    def __repr__(self) -> str:
        attrs = [
            ('id', self.id),
            ('name', self.name),
            ('is_active', self.is_active),
            ('start_time', self.start_time),
            ('end_time', self.end_time),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def _update(self, data: Any) -> None:
        self.id: str = data['ID']
        self.name: str = data['Name']
        self.is_active: bool = data['IsActive']
        self._start_time: str = data['StartTime']
        self._end_time: str = data['EndTime']

    @property
    def start_time(self) -> datetime:
        return utils.parse_iso_datetime(self._start_time)

    @property
    def end_time(self) -> datetime:
        return utils.parse_iso_datetime(self._end_time)

class ContentTier(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<ContentTier name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Optional[Union[str, Dict[str, str]]] = data['displayName']
        self.dev_name: str = data['devName']
        self.rank: int = data['rank']
        self.juice_value: int = data['juiceValue']
        self.juice_cost: int = data['juiceCost']
        self.highlight_color: str = data['highlightColor']
        self._display_icon: str = data['displayIcon']
        self.asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the content tier's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the content tier's name."""
        return self.name_localizations.american_english

    @property
    def highlight_color_rgb(self) -> str:
        """:class: `str` Returns the content tier's highlight color RGB."""
        # rgba to rgb
        return self.highlight_color[:-1]

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the content tier's icon."""
        return Asset._from_url(self._client, self._display_icon)
