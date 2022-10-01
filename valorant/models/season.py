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

from locale import str
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Mapping

from .. import utils
from ..asset import Asset
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    import datetime

    from typing_extensions import Self

    from ..client import Client
    from .competitive import CompetitiveTier

__all__ = (
    'Season',
    'SeasonCompetitive',
)


class Season(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._type: Optional[str] = data.get('type')
        self._start_time_iso: Union[str, datetime.datetime] = data['startTime']
        self._end_time_iso: Union[str, datetime.datetime] = data['endTime']
        self._parent_uuid: str = data['parentUuid']
        self.asset_path: str = data['assetPath']

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        attrs = [('display_name', self.display_name), ('type', self.type)]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the season's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the season's name."""
        return self.name_localizations.american_english

    @property
    def type(self) -> Optional[str]:
        """:class: `str` Returns the season's type."""
        return self._type.removeprefix('EAresSeasonType::') if self._type else None

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


class Border:
    def __init__(self, client: Client, data: Dict[str, Any]) -> None:
        self._client = client
        self.uuid: str = data['uuid']
        self.level: int = data['level']
        self.wins_required: int = data['winsRequired']
        self._display_icon: Optional[str] = data['displayIcon']
        self._small_icon: Optional[str] = data['smallIcon']
        self.asset_path: str = data['assetPath']

    def __repr__(self) -> str:
        attrs = [('level', self.level), ('wins_required', self.wins_required)]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the border's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon) if self._display_icon else None

    @property
    def small_icon(self) -> Asset:
        """:class: `Asset` Returns the border's small icon."""
        return Asset._from_url(client=self._client, url=self._small_icon) if self._small_icon else None


class SeasonCompetitive:
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        self._client = client
        self._uuid: str = data['uuid']
        self._start_time_iso: Union[str, datetime.datetime] = data['startTime']
        self._end_time_iso: Union[str, datetime.datetime] = data['endTime']
        self._season_uuid: str = data['seasonUuid']
        self._competitive_tiers_uuid: str = data['competitiveTiersUuid']
        self.borders: List[Border] = [Border(client=self._client, data=b) for b in data['borders']]

    def __repr__(self) -> str:
        attrs = [
            ('start_time', self.start_time),
            ('end_time', self.end_time),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def start_time(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the season's start time."""
        return utils.parse_iso_datetime(self._start_time_iso)

    @property
    def end_time(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the season's end time."""
        return utils.parse_iso_datetime(self._end_time_iso)

    @property
    def season(self) -> Optional[Season]:
        """:class: `Season` Returns the season."""
        # TODO: get from _client
        return Season._from_uuid(client=self._client, uuid=self._season_uuid)

    @property
    def competitive_tiers(self) -> Optional[CompetitiveTier]:
        """:class: `CompetitiveTier` Returns the competitive tiers."""
        return self._client.get_competitive_tier(uuid=self._competitive_tiers_uuid)
