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

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from ..types.player import (
        NameService as NameServicePayload,
        PartialPlayer as PartialPlayerPayload,
        Player as PlayerPayload,
    )
    from .level_border import LevelBorder
    from .player_card import PlayerCard
    from .player_title import PlayerTitle

__all__ = ('Player', 'ClientPlayer', 'NameService')


class _PlayerTag:
    __slots__ = ()
    puuid: str


class Player(_PlayerTag):

    # __slots__ = ()

    if TYPE_CHECKING:
        name: str
        # puuid: str
        _puuid: Optional[str]
        tag: str
        region: str
        _client: Client
        _player_card_id: Optional[str]
        _player_title_id: Optional[str]
        _level_border_id: Optional[str]
        _last_updated: Optional[datetime.datetime]

    def __init__(
        self,
        *,
        client: Client,
        data: Union[PlayerPayload, PartialPlayerPayload, Any],
    ) -> None:
        self._client = client
        self._puuid: str = data.get('puuid', None) or data.get('Subject') or data.get('subject', None)
        self.name: Optional[str] = data.get('username') or data.get('gameName')
        self.tag: Optional[str] = data.get('tagline') or data.get('tagLine')
        self.region: Optional[str] = data.get('region')
        self.account_level: int = 0
        self._player_card: Optional[PlayerCard] = None
        self._player_title: Optional[PlayerTitle] = None
        self._level_border: Optional[LevelBorder] = None
        self._last_updated: Optional[datetime.datetime] = None

    def __str__(self) -> str:
        return f'{self.name}#{self.tag}'

    def __repr__(self) -> str:
        return f"<Player puuid={self.puuid!r} name={self.name!r} tagline={self.tag!r} region={self.region!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _PlayerTag) and other.puuid == self.puuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.puuid)

    @property
    def puuid(self) -> str:
        # if not self._puuid:
        #     self._puuid = self._client.fetch_player_by_name(self.name, self.tagline)
        return self._puuid

    @property
    def display_name(self) -> str:
        if self.name is None and self.tag is None:
            return 'Unknown'
        return f"{self.name}#{self.tag}"

    @property
    def player_card(self) -> Optional[PlayerCard]:
        return self._player_card

    @player_card.setter
    def player_card(self, value: Optional[PlayerCard]) -> None:
        self._player_card = value

    @property
    def player_title(self) -> Optional[PlayerTitle]:
        return self._player_title

    @player_title.setter
    def player_title(self, value: Optional[PlayerTitle]) -> None:
        self._player_title = value

    @property
    def level_border(self) -> Optional[LevelBorder]:
        return self._level_border

    @level_border.setter
    def level_border(self, value: Optional[LevelBorder]) -> None:
        self._level_border = value

    @property
    def mmr(self) -> int:
        return self.mmr

    @property
    def last_update(self) -> datetime.datetime:
        return self._last_updated

    @last_update.setter
    def last_update(self, value: datetime.datetime) -> None:
        self._last_updated = value

    async def fetch_data(self) -> Self:
        match_history = await self._client.fetch_match_history(puuid=self.puuid, end=1)
        for match in match_history:
            for player in match.players:
                if player.puuid == self.puuid:
                    self.name = player.name
                    self.tag = player.tag
                    self.player_card = player.player_card
                    self.player_title = player.player_title
                    self.level_border = player.level_border
                    self.account_level = player.account_level
                    self.last_update = match.started_at
                    # TODO: return rank
        return self

    def parse_name_tag(self, name: str, tag: str) -> None:
        self.name = name
        self.tag = tag


class ClientPlayer(Player):
    def __init__(self, *, client: Client, data: Union[PlayerPayload, Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)
        self.locale: str = data.get('locale', None)

    def __repr__(self) -> str:
        return f'<ClientPlayer puuid={self.puuid!r} name={self.name!r} tagline={self.tag!r} region={self.region!r}'


class NameService:
    def __init__(self, data: NameServicePayload) -> None:
        self._display_name: str = data.get('DisplayName')
        self.puuid: str = data.get('Subject')
        self.name: str = data.get('GameName')
        self.tag: str = data.get('TagLine')

    def __repr__(self) -> str:
        return f'<NameService tag={self.tag!r} name={self.name!r}>'
