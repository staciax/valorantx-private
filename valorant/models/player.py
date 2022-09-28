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
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ..enums import LevelBorderID

if TYPE_CHECKING:
    from ..client import Client
    from ..types.player import PartialPlayer as PartialPlayerPayload, Player as PlayerPayload
    from .level_border import LevelBorder
    from .player_card import PlayerCard
    from .player_title import PlayerTitle

# fmt: off
__all__ = (
    'BasePlayer',
    'ClientPlayer',
)
# fmt: on


class _PlayerTag:
    __slots__ = ()
    puuid: str


class BasePlayer(_PlayerTag):

    __slots__ = (
        'name',
        '_puuid',
        'tagline',
        'region',
        '_client',
        'account_level',
        '_player_card_id',
        '_player_title_id',
        '_level_border_id',
    )

    if TYPE_CHECKING:
        name: str
        # puuid: str
        _puuid: Optional[str]
        tagline: str
        region: str
        _client: Client
        _player_card_id: Optional[str]
        _player_title_id: Optional[str]
        _level_border_id: Optional[str]

    def __init__(
        self,
        *,
        client: Client,
        data: Union[PlayerPayload, PartialPlayerPayload],
    ) -> None:
        self._client = client
        self._puuid: str = data.get('puuid', None) or data.get('Subject', None) or data.get('subject', None)
        self._update(data)

    def __str__(self) -> str:
        return f'{self.name}#{self.tagline}'

    def __repr__(self) -> str:
        return f"<Player puuid={self.puuid!r} name={self.name!r} tagline={self.tagline!r} region={self.region!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _PlayerTag) and other.puuid == self.puuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.puuid)

    def _update(self, data: Union[PlayerPayload, PartialPlayerPayload]) -> None:
        self.name: Optional[str] = data.get('username', None) or data.get('gameName', None)
        self.tagline: Optional[str] = data.get('tagline', None) or data.get('tagLine', None)
        self.region: Optional[str] = data.get('region', None)
        self.account_level: int = 0
        self._player_card_id: Optional[str] = None
        self._player_title_id: Optional[str] = None
        self._level_border_id: Optional[str] = None

    @property
    def puuid(self) -> str:
        # if not self._puuid:
        #     self._puuid = self._client.fetch_player_by_name(self.name, self.tagline)
        return self._puuid

    @property
    def display_name(self) -> str:
        if self.name is None and self.tagline is None:
            return 'Unknown'
        return f"{self.name}#{self.tagline}"

    @property
    def player_card(self) -> Optional[PlayerCard]:
        return self._client.get_player_card(uuid=self._player_card_id)

    @property
    def player_title(self) -> Optional[PlayerTitle]:
        return self._client.get_player_title(uuid=self._player_title_id)

    @property
    def level_border(self) -> Optional[LevelBorder]:
        return self._client.get_level_border(uuid=self._level_border_id) or self._client.get_level_border(
            uuid=str(LevelBorderID._1)
        )

    @property
    def mmr(self) -> int:
        return self.mmr

    @property
    def last_update(self) -> datetime:
        return ...


class ClientPlayer(BasePlayer):
    def __init__(self, *, client: Client, data: Union[PlayerPayload, Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)
        self.locale: str = data.get('locale', None)

    def __repr__(self) -> str:
        return f'<ClientPlayer puuid={self.puuid!r} name={self.name!r} tagline={self.tagline!r} region={self.region!r}'
