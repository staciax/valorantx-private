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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Mapping

from .. import utils
from ..enums import MissionType, try_enum
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from ..types.contract import Mission as MissionUPayload, MissionMeta as MissionMetaPayload

# fmt: off
__all__ = (
    'Mission',
    'MissionU',
    'MissionMeta',
)
# fmt: on


class Mission(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Optional[Union[str, Dict[str, str]]] = data['displayName']
        self._title: Optional[Union[str, Dict[str, str]]] = data['title']
        self._type: Optional[str] = data['type']
        self.xp: int = data['xpGrant']
        self.progress_to_complete: int = data['progressToComplete']
        self._activation_date_iso: str = data['activationDate']
        self._expiration_date_iso: str = data['expirationDate']
        self.tags: Optional[List[str]] = data['tags']
        self.objectives: List[Dict[str, Any]] = data.get('objectives', [])
        self.asset_path: str = data['assetPath']

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f'<Mission title={self.title!r}>'

    def __int__(self) -> int:
        return self.xp

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
    def type(self) -> Optional[MissionType]:
        """Optional[:class: `MissionType`] Returns the mission's type."""
        if self._type is None:
            return None
        type_strip = self._type.removeprefix('EAresMissionType::')
        return try_enum(MissionType, type_strip)

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


class MissionU(Mission):
    def __init__(self, client: Client, data: Mapping[str, Any], mission: MissionUPayload) -> None:
        super().__init__(client=client, data=data)
        self._objectives: Dict[str, int] = mission['Objectives']
        self._complete: bool = mission['Complete']
        self._expiration_time_iso: str = mission['ExpirationTime']
        self.current_progress: int = 0
        self.left_progress: int = 0
        self.total_progress: int = 0
        self._mission_update()

    def __repr__(self) -> str:
        return f'<MissionU title={self.title!r} complete={self.is_completed()!r}>'

    def _mission_update(self) -> None:
        if len(self.objectives) > 0:
            objectives_uuid = self.objectives[0]['objectiveUuid']
            objectives_value = self.objectives[0]['value']

            # if self.progress_to_complete < objectives_value: # Bugged
            #     self.current_progress = self._objectives[objectives_uuid]

            self.current_progress = self._objectives[objectives_uuid]
            self.left_progress = objectives_value - self.current_progress
            self.total_progress = objectives_value

    @property
    def progress(self) -> int:
        """:class: `int` Returns the mission's progress."""
        return self.current_progress

    @property
    def target(self) -> int:
        """:class: `int` Returns the mission's target."""
        return self.total_progress

    def is_completed(self) -> bool:
        """:class: `bool` Returns whether the mission is complete."""
        return self._complete

    @property
    def expiration_time(self) -> Optional[datetime.datetime]:
        """:class: `datetime.datetime` Returns the contract's expiration time."""
        return utils.parse_iso_datetime(self._expiration_time_iso) if self._expiration_time_iso else None

    @classmethod
    def _from_mission(cls, client: Client, mission: MissionUPayload) -> Optional[Self]:
        """Returns the mission with the given UUID."""
        data = client.assets.get_mission(mission['ID'])
        return cls(client=client, data=data, mission=mission) if data else None


class MissionMeta:
    def __init__(self, data: MissionMetaPayload) -> None:
        self.NPE_completed: bool = data.get('NPECompleted', False)
        self._weekly_check_point: Union[datetime, str] = data.get('WeeklyCheckpoint')
        self._weekly_refill_time: Union[datetime, str] = data.get('WeeklyRefillTime')

    def __bool__(self) -> bool:
        return self.NPE_completed

    def __repr__(self) -> str:
        attrs = [
            ('NPE_completed', self.NPE_completed),
            ('weekly_check_point', self.weekly_check_point),
            ('weekly_refill_time', self.weekly_refill_time),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def weekly_check_point(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the weekly check point."""
        return utils.parse_iso_datetime(self._weekly_check_point)

    @property
    def weekly_refill_time(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the weekly refill time."""
        return utils.parse_iso_datetime(self._weekly_refill_time)
