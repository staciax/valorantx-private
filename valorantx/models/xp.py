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
from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Union

from .. import utils

if TYPE_CHECKING:
    from ..client import Client
    from ..types.xp import (
        AccountXP as AccountXPPayload,
        AccountXPHistory as AccountXPHistoryPayload,
        AccountXPProgress as AccountXPProgressPayload,
    )
    from .match import MatchDetails

# fmt: off
__all__ = (
    'AccountXP',
)
# fmt: on


class SourceXP:
    def __init__(self, data: Mapping[str, Any]):
        self.id: str = data['ID']
        self.amount: int = data['Amount']

    def __repr__(self) -> str:
        return f'<SourceXP id={self.id!r} amount={self.amount!r}>'

    def __int__(self) -> int:
        return self.amount

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SourceXP) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        return isinstance(other, SourceXP) and self.amount < other.amount

    def __le__(self, other: object) -> bool:
        return isinstance(other, SourceXP) and self.amount <= other.amount

    def __gt__(self, other: object) -> bool:
        return isinstance(other, SourceXP) and self.amount > other.amount

    def __ge__(self, other: object) -> bool:
        return isinstance(other, SourceXP) and self.amount >= other.amount


class ProgressXP:
    def __init__(self, data: AccountXPProgressPayload):
        self.level: int = data['Level']
        self.xp: int = data['XP']

    def __repr__(self) -> str:
        return f'<ProgressXP level={self.level!r} xp={self.xp!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ProgressXP) and other.level == self.level and other.xp == self.xp

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        return isinstance(other, ProgressXP) and self.level < other.level and self.xp < other.xp

    def __le__(self, other: object) -> bool:
        return isinstance(other, ProgressXP) and self.level <= other.level and self.xp <= other.xp

    def __gt__(self, other: object) -> bool:
        return isinstance(other, ProgressXP) and self.level > other.level and self.xp > other.xp

    def __ge__(self, other: object) -> bool:
        return isinstance(other, ProgressXP) and self.level >= other.level and self.xp >= other.xp


class HistoryXP:
    def __init__(self, client: Client, data: AccountXPHistoryPayload):
        self._client: Client = client
        self.id: str = data['ID']
        self.match_start: datetime.datetime = utils.parse_iso_datetime(str(data['MatchStart']))
        self.start_progress: ProgressXP = ProgressXP(data['StartProgress'])
        self.end_progress: ProgressXP = ProgressXP(data['EndProgress'])
        self.xp_delta: int = data['XPDelta']
        self.xp_sources: List[SourceXP] = [SourceXP(source) for source in data['XPSources']]
        self.xp_multipliers: List[Any] = data['XPMultipliers']

    def __repr__(self) -> str:
        attrs = [
            ('id', self.id),
            ('match_start', self.match_start),
            ('start_progress', self.start_progress),
            ('end_progress', self.end_progress),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    async def fetch_match_details(self) -> Optional[MatchDetails]:
        return await self._client.fetch_match_details(self.id)


class AccountXP:
    def __init__(self, client: Client, data: AccountXPPayload) -> None:
        self._client = client
        self.version: int = data['Version']
        self.subject: str = data['Subject']
        self.progress: ProgressXP = ProgressXP(data['Progress'])
        self.history: List[HistoryXP] = [HistoryXP(client, history) for history in data['History']]
        self._last_time_granted_first_win_iso: Union[str, datetime.datetime] = data['LastTimeGrantedFirstWin']
        self._next_time_first_win_available_iso: Union[str, datetime.datetime] = data['NextTimeFirstWinAvailable']

    def __repr__(self) -> str:
        return f'<AccountXP version={self.version!r} subject={self.subject!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.version == other.version and self.subject == other.subject

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def level(self) -> int:
        """:class:`int`: The current level of the account."""
        return self.progress.level

    @property
    def xp(self) -> int:
        """:class:`int`: The current XP of the account."""
        return self.progress.xp

    @property
    def last_time_granted_first_win(self) -> datetime.datetime:
        """
        :class: `datetime.datetime` Returns the last time the player was granted the first win.
        """
        return utils.parse_iso_datetime(str(self._last_time_granted_first_win_iso))

    @property
    def next_time_first_win_available(self) -> datetime.datetime:
        """
        :class: `datetime.datetime`
        Returns the next time the player can be granted the first win.
        """
        return utils.parse_iso_datetime(str(self._next_time_first_win_available_iso))
