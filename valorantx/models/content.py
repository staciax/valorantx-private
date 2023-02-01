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
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Union

from .. import utils
from ..asset import Asset
from ..enums import Locale
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

__all__ = ('Content', 'ContentEvent', 'ContentSeason', 'ContentTier')


class Content:
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        self._client = client
        self._disabled_ids: List[str] = data['DisabledIDs']
        self._seasons: List[Optional[Mapping[str, Any]]] = data['Seasons']
        self._events: List[Optional[Mapping[str, Any]]] = data['Events']

    def __repr__(self) -> str:
        return f"<Content season={self.get_seasons()!r}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Content) and (
            self.disabled_ids == other.disabled_ids
            and self.get_seasons() == other.get_seasons()
            and self.get_events() == other.get_events()
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def disabled_ids(self) -> List[str]:
        return self._disabled_ids

    def get_seasons(self) -> List[ContentSeason]:
        return [ContentSeason(season) for season in self._seasons if season is not None]

    def get_events(self) -> List[ContentEvent]:
        return [ContentEvent(event) for event in self._events if event is not None]


class ContentSeason:
    def __init__(self, data: Mapping[str, Any]) -> None:
        self.id: str = data['ID']
        self.name: str = data['Name']
        self.type: str = data['Type']
        self._is_active: bool = data['IsActive']
        self._start_time: str = data['StartTime']
        self._end_time: str = data['EndTime']

    def __repr__(self) -> str:
        return f"<ContentSeason name={self.name!r} type={self.type!r} is_active={self.is_active()!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ContentSeason) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def is_active(self) -> bool:
        """:class:`bool` Returns whether the season is active."""
        return self._is_active

    @property
    def start_time(self) -> datetime.datetime:
        """:class:`datetime.datetime` Returns the start time of the season."""
        return utils.parse_iso_datetime(self._start_time)

    @property
    def end_time(self) -> datetime.datetime:
        """:class:`datetime.datetime` Returns the end time of the season."""
        return utils.parse_iso_datetime(self._end_time)


class ContentEvent:
    def __init__(self, data: Mapping[str, Any]) -> None:
        self.id: str = data['ID']
        self.name: str = data['Name']
        self._is_active: bool = data['IsActive']
        self._start_time: str = data['StartTime']
        self._end_time: str = data['EndTime']

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

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ContentEvent) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def is_active(self) -> bool:
        """:class:`bool` Returns whether the event is active."""
        return self._is_active

    @property
    def start_time(self) -> datetime.datetime:
        """:class:`datetime.datetime` Returns the start time of the event."""
        return utils.parse_iso_datetime(self._start_time)

    @property
    def end_time(self) -> datetime.datetime:
        """:class:`datetime.datetime` Returns the end time of the event."""
        return utils.parse_iso_datetime(self._end_time)


class ContentTier(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Optional[Dict[str, str]] = data['displayName']
        self.dev_name: str = data['devName']
        self.rank: int = data['rank']
        self.juice_value: int = data['juiceValue']
        self.juice_cost: int = data['juiceCost']
        self.highlight_color: str = data['highlightColor']
        self._display_icon: str = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=client.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<ContentTier display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the content tier's name."""
        return self._display_name_localized

    @property
    def highlight_color_rgb(self) -> str:
        """:class: `str` Returns the content tier's highlight color RGB."""
        # rgba to rgb
        return self.highlight_color[:-1]

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the content tier's icon."""
        return Asset._from_url(self._client, self._display_icon)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the content tier with the given UUID."""
        data = client._assets.get_content_tier(uuid)
        return cls(client=client, data=data) if data else None
