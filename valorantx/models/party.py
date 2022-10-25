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

from typing import TYPE_CHECKING, Any, Dict, List

from .player import Player

if TYPE_CHECKING:
    from ..client import Client

    if TYPE_CHECKING:
        from ..client import Client
        from ..types.party import PlayerParty as PlayerPartyPayload

# fmt: off
__all__ = (
    'PlayerParty',
)
# fmt: on


class Ping:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.game_pod_id: str = data['GamePodID']
        self.ping: Any = data['Ping']

    # @staticmethod
    # def __get_server_ping(game_pod_id: str) -> str:
    #     server_name = game_pod_id.split('-')[5]
    #     server_number = game_pod_id.split('-')[6]
    #     return f"{server_name}-{server_number}"

    # TODO: function strip out the ping data and return it as a string


class PlayerParty(Player):
    """
    A player that is currently in a party.

    .. container:: operations

        .. describe:: x == y

            Checks if two players are equal.

        .. describe:: x != y

            Checks if two players are not equal.

        .. describe:: str(x)

            Returns a string representation of the player.
    """

    __slots__ = ('_is_owner', '_is_ready', 'is_moderator', 'platform_type', '_pings')

    def __init__(self, *, client: Client, data: PlayerPartyPayload) -> None:
        super().__init__(client=client, data=data)
        self._is_owner: bool = data.get('IsOwner', False)
        self._is_ready: bool = data.get('IsReady', False)
        self.is_moderator: bool = data.get('IsModerator', False)
        self.platform_type: str = data['PlatformType']
        self._pings: List[Any] = data.get('Pings', [])

    def __repr__(self) -> str:
        return f'<PlayerParty puuid={self.puuid!r} name={self.name!r} tagline={self.tagline!r} region={self.region!r}>'

    def is_owner(self) -> bool:
        """
        :class: `bool`
        Returns whether the player is the party owner.
        """
        return self._is_owner

    def is_ready(self) -> bool:
        """
        :class: `bool`
        Returns whether the player is ready to play.
        """
        return self._is_ready

    @property
    def pings(self) -> List[Ping]:
        return [Ping(ping) for ping in self._pings]
