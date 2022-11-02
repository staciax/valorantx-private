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

from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Union

from ..errors import PartyNotOwner
from .match import Platform
from .player import Player

if TYPE_CHECKING:
    from ..client import Client

    if TYPE_CHECKING:
        from ..client import Client
        from ..enums import QueueID
        from ..types.party import Party as PartyPayload, PlayerParty as PlayerPartyPayload

# fmt: off
__all__ = (
    'PlayerParty',
)
# fmt: on


class PartyPlayer:
    def __init__(self, *, client: Client, data: PartyPayload) -> None:
        self._client = client
        self._subject: str = data.get('Subject')
        self._version: int = data.get('Version')
        self.id: str = data.get('CurrentPartyID')
        self.invites: Optional[Any] = data.get('Invites')
        self.requests: List[Any] = data.get('Requests')
        self._platform_info: Any = data.get('PlatformInfo')

    def __repr__(self) -> str:
        return f'<PartyPlayer id={self.id!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PartyPlayer) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Party:
    def __init__(self, *, client: Client, data: Mapping[str, Any]) -> None:
        self._client = client
        self.id: str = ...
        self._is_owner: bool = False

    async def remove_player(self, player: Union[str, Player]) -> None:
        """|coro|

        Remove a player from the party.

        Parameters
        ----------
        player: Union[:class:`str`, :class:`Player`]
            The player to remove from the party.
        """
        puuid = player if isinstance(player, str) else player.puuid
        await self._client.http.party_remove_player(puuid=puuid)

    async def invite_player_by_display_name(self, player: Union[str, Player]) -> None:
        """|coro|

        Invite a player to the party by their display name.

        Parameters
        ----------
        player: Union[:class:`str`, :class:`Player`]
            The player to invite to the party.
        """

        if isinstance(player, Player):
            player = player.display_name
        else:
            player = player

        name, tag = player.split('#')

        await self._client.http.party_invite_by_display_name(
            party_id=self.id,
            name=name,
            tag=tag,
        )

    async def decline_invite(self, request_id: str) -> None:
        """|coro|

        Decline an invite to a party.

        Parameters
        ----------
        request_id: :class:`str`
            The request ID of the invite.
        """

        await self._client.http.party_decline_request(party_id=self.id, request_id=request_id)

    async def leave(self) -> None:
        """|coro|

        Leave the party.
        """

        await self._client.http.party_leave(party_id=self.id)

    async def change_queue(self, queue_id: Optional[QueueID, str] = None) -> None:
        """|coro|

        Change the queue of the party.

        Parameters
        ----------
        queue_id: Optional[:class:`Union[QueueID, str]`]
            The queue to change to. If ``None``, the queue will be set to ``None``.
        """

        if not self.is_owner():
            raise PartyNotOwner('You must be the owner of the party to change the queue.')

        if queue_id is not None:
            await self._client.http.party_change_queue(party_id=self.id, queue_id=queue_id)

    async def enter_matchmaking_queue(self) -> None:
        """|coro|

        Enter the matchmaking queue.
        """

        if not self.is_owner():
            raise PartyNotOwner('You must be the owner of the party to enter the matchmaking queue.')

        await self._client.http.party_enter_matchmaking_queue(party_id=self.id)

    async def leave_matchmaking_queue(self) -> None:
        """|coro|

        Leave the matchmaking queue.
        """

        if not self.is_owner():
            raise PartyNotOwner('You must be the owner of the party to leave the matchmaking queue.')

        await self._client.http.party_leave_matchmaking_queue(party_id=self.id)

    async def transfer_owner(self, player: Union[str, Player]) -> None:
        """|coro|

        Transfer the owner of the party to the given player.

        Parameters
        ----------
        player: Union[:class:`str`, :class:`Player`]
            The player to transfer the owner to.
        """

        if not self.is_owner():
            raise PartyNotOwner('You must be the owner of the party to transfer the owner.')

        puuid = player if isinstance(player, str) else player.puuid
        await self._client.http.party_transfer_owner(party_id=self.id, puuid=puuid)

    async def set_accessibility(self, open_join: bool) -> None:
        """|coro|

        Set the party accessibility.
        """

        if not self.is_owner():
            raise PartyNotOwner('You must be the owner of the party to set the accessibility.')

        await self._client.http.set_party_accessibility(party_id=self.id, open_join=open_join)

    def is_owner(self) -> bool:
        """:class:`bool`: Whether the client is the owner of the party."""
        return self._is_owner

    # async def accept_invite(self, request_id: str) -> None:
    #     await self._client.http.party_

    # async def invite_player(self, player: Union[str, Player]) -> None:
    #     await self._client.http.party


class Ping:
    def __init__(self, data: Mapping[str, Any]) -> None:
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
