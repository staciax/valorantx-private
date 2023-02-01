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

from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ..enums import Region, try_enum
from ..errors import InvalidPuuid, PartyNotOwner
from ..utils import is_uuid

# from .match import Platform
from .player import Player

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

    if TYPE_CHECKING:
        from ..client import Client
        from ..enums import QueueType
        from ..types.party import (
            MatchmakingData as MatchmakingDataPayload,
            Party as PartyPayload,
            PartyMember as PlayerPartyPayload,
            PartyPlayer as PartyPlayerPayload,
            Ping as PingPayload,
        )

__all__ = (
    'Party',
    'PartyPlayer',
    'PlayerParty',
)


class PartyPlayer:
    def __init__(self, *, client: Client, data: PartyPlayerPayload) -> None:
        self._client = client
        self._subject: str = data.get('Subject')
        self._version: int = data.get('Version')
        self.id: str = data.get('CurrentPartyID')
        self.invites: Optional[Any] = data.get('Invites')
        self.requests: List[Any] = data.get('Requests')
        self._platform_info: Any = data.get('PlatformInfo')
        self._current_queue: Optional[QueueType] = None

    def __repr__(self) -> str:
        return f'<PartyPlayer id={self.id!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PartyPlayer) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class CustomGameData:
    pass


class Matchmaking:
    def __init__(self, data: MatchmakingDataPayload) -> None:
        self.queue: QueueType = try_enum(QueueType, data.get('QueueID'))
        self.preferred_game_pods: List[str] = data.get('PreferredGamePods')
        self.skill_disparity_rr_penalty: int = data.get('SkillDisparityRRPenalty')

    def __eq__(self, other: Matchmaking) -> bool:
        return isinstance(other, Matchmaking) and other.queue == self.queue

    def __ne__(self, other: Matchmaking) -> bool:
        return not self.__eq__(other)


class Party:
    id: str
    muc_name: str
    voice_room_id: str
    version: int
    client_version: str
    state: str
    previous_state: str
    state_transition_reason: str
    accessibility: str
    matchmaking: Matchmaking

    def __init__(self, *, client: Client, data: PartyPayload) -> None:
        self._client = client
        self._is_owner: bool = False
        self._members: List[PlayerParty] = []
        self._party_owner: Optional[PlayerParty] = None
        self._current_queue: Optional[QueueType] = None
        self._closed: bool = False
        self._members_cache: Dict[str, PlayerParty] = {}
        self._update(data)

    def __repr__(self) -> str:
        return f'<Party id={self.id!r} members={self._members!r}>'

    def _update(self, data: PartyPayload) -> None:
        self.id: str = data.get('ID')
        self.muc_name: str = data.get('MUCName')
        self.voice_room_id: str = data.get('VoiceRoomID')
        self.version: int = data.get('Version')
        self.client_version: str = data.get('ClientVersion')
        self.state: str = data.get('State')
        self.previous_state: str = data.get('PreviousState')
        self.state_transition_reason: str = data.get('StateTransitionReason')
        self.accessibility: str = data.get('Accessibility')
        self.matchmaking: Matchmaking = Matchmaking(data.get('MatchmakingData'))
        self._current_queue = self.matchmaking.queue
        self._is_owner: bool = False
        self._members: List[PlayerParty] = [
            PlayerParty(client=self._client, data=member) for member in data.get('Members', [])
        ]
        self._party_owner: Optional[PlayerParty] = next((member for member in self._members if member.is_owner()), None)
        self._closed: bool = self.accessibility == 'CLOSED'

        for member in self._members:
            try_member = self._members_cache.get(member.puuid)
            if try_member:
                member.parse_name_tag(try_member.name, try_member.tag)
                member.region = try_member.region
            else:
                self._members_cache[member.puuid] = member

    async def update_member_display_name(self) -> None:
        """|coro|

        Update the display name of members in the party.
        """
        puuid_list = [member.puuid for member in self._members if member.name is None or member.tag is None]
        if len(puuid_list) > 0:
            name_service = await self._client.fetch_name_by_puuid(puuid=puuid_list)
            for member in self._members:
                for name in name_service:
                    if member.puuid == name.puuid:
                        member.parse_name_tag(name.name, name.tag)
                        member.region = self._client.user.region

    async def refresh(self) -> Self:
        """|coro|

        Refreshes the party data.
        """
        party = await self._client.http.fetch_party(party_id=self.id)
        self._update(party)
        await self.update_member_display_name()
        return self

    def get_members(self) -> List[PlayerParty]:
        """Get the members of the party.

        Returns
        -------
        List[:class:`PlayerParty`]
            The members of the party.
        """
        return self._members

    def get_current_queue(self) -> Optional[QueueType]:
        """Get the current queue of the party.

        Returns
        -------
        :class:`QueueType`
            The current queue of the party.
        """
        return self._current_queue

    async def remove_player(self, player: Union[str, PlayerParty]) -> None:
        """|coro|

        Remove a player from the party.

        Parameters
        ----------
        player: Union[:class:`str`, :class:`PlayerParty`]
            The player to remove from the party.
        """

        if player == self._client.user:
            return

        if not self.is_owner():
            raise PartyNotOwner('You are not the owner of the party.')

        puuid = player if isinstance(player, str) else player.puuid
        if not is_uuid(puuid):
            raise InvalidPuuid("Player puuid is invalid")
        await self._client.http.party_remove_player(puuid=puuid)

    async def invite_by_display_name(self, display_name: str) -> None:
        """|coro|

        Invite a player to the party by their display name.

        Parameters
        ----------
        display_name: :class:`str`
            The display name of the player to invite.
        """

        name, tag = display_name.split('#')

        # TODO: check party is full

        await self._client.http.party_invite_by_display_name(
            party_id=self.id,
            name=name,
            tag=tag,
        )

    async def decline_invite(self, request_id: str) -> None:
        """|coro|

        Decline an invitation to a party.

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

    async def change_queue(self, queue: Optional[Union[QueueType, str]] = None) -> None:
        """|coro|

        Change the queue of the party.

        Parameters
        ----------
        queue: Optional[:class:`Union[QueueType, str]`]
            The queue to change to. If ``None``, the queue will be set to ``None``.
        """

        if not self.is_owner():
            raise PartyNotOwner('You must be the owner of the party to change the queue.')

        if queue is not None:
            party = await self._client.http.party_change_queue(party_id=self.id, queue_id=queue)
            self._update(party)
            await self.update_member_display_name()

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

    async def transfer_owner(self, player: Union[str, PlayerParty]) -> None:
        """|coro|

        Transfer the owner of the party to the given player.

        Parameters
        ----------
        player: Union[:class:`str`, :class:`Player`]
            The player to transfer the owner to.

        Raises
        ------
        PartyNotOwner
            You must be the owner of the party to transfer the owner.
        """

        if not self.is_owner():
            raise PartyNotOwner('You must be the owner of the party to transfer the owner.')

        if self._party_owner == self._client.user:
            raise PartyNotOwner('You cannot transfer the owner to yourself.')

        puuid = player if isinstance(player, str) else player.puuid

        if not is_uuid(puuid):
            raise InvalidPuuid("Player puuid is invalid")

        await self._client.http.party_transfer_owner(party_id=self.id, puuid=puuid)

    async def set_accessibility(self, open_join: bool) -> None:
        """|coro|

        Set the party accessibility.
        """

        if not self.is_owner():
            raise PartyNotOwner('You must be the owner of the party to set the accessibility.')

        party = await self._client.http.set_party_accessibility(party_id=self.id, open_join=open_join)
        self._update(party)
        await self.update_member_display_name()

    async def refresh_identity(self) -> None:
        """|coro|

        Refresh the identity of the party.
        """
        await self._client.http.party_refresh_player_identity(party_id=self.id)

    def is_owner(self) -> bool:
        """:class:`bool`: Whether the client is the owner of the party."""
        return self._party_owner == self._client.user

    def get_party_owner(self) -> Optional[PlayerParty]:
        """:class:`PlayerParty`: The owner of the party."""
        return self._party_owner

    def is_closed(self) -> bool:
        """:class:`bool`: Whether the party is closed."""
        return self._closed

    # def party_is_full(self) -> bool:
    #     """:class:`bool`: Whether the party is full."""
    #     return len(self._members) >= 5

    # async def accept_invite(self, request_id: str) -> None:
    #     await self._client.http.party_

    # async def invite_player(self, player: Union[str, Player]) -> None:
    #     await self._client.http.party


class Ping:
    def __init__(self, data: PingPayload) -> None:
        self.game_pod_id: str = data.get('GamePodID')
        self.ping: int = data.get('Ping')

    @cached_property
    def region(self) -> Region:
        pod_split = self.game_pod_id.split('-')
        region_str = pod_split[-4].removeprefix('prod.')
        return try_enum(Region, region_str)

    @cached_property
    def server(self) -> str:
        return self.game_pod_id.split('-')[-2] + ' ' + self.game_pod_id.split('-')[-1]


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

    def __init__(self, *, client: Client, data: PlayerPartyPayload) -> None:
        super().__init__(client=client, data=data)
        self.pings: List[Ping] = []
        self._is_owner: bool = False
        self._is_ready: bool = False
        self._is_moderator: bool = False
        self._use_broadcast_hud: bool = False
        self.is_moderator: bool = False
        self._incognito: bool = False
        self._hide_account_level: bool = False
        self.platform_type: str = data.get('PlatformType', 'PC')
        # self.competitive_tier: Any = now season
        self._update(data=data)

    def __repr__(self) -> str:
        return f'<PlayerParty name={self.name!r} tag={self.tag!r} region={self.region!r}>'

    def _update(self, data: PlayerPartyPayload) -> None:
        self._is_owner = data.get('IsOwner', self._is_owner)
        self._is_ready = data.get('IsReady', self._is_ready)
        self._is_moderator = data.get('IsModerator', self._is_moderator)
        self._use_broadcast_hud = data.get('UseBroadcastHUD', self._use_broadcast_hud)

        self._pings = [Ping(ping) for ping in data.get('Pings', [])]

        # identity

        identity = data['PlayerIdentity']

        player_card = self._client.get_player_card(uuid=identity.get('PlayerCardID'))
        if player_card is not None:
            self._player_card = player_card

        player_title = self._client.get_player_title(uuid=identity.get('PlayerTitleID'))
        if player_title is not None:
            self._player_title = player_title

        level_border = self._client.get_level_border(startingLevel=identity.get('PreferredLevelBorderID', 0))
        if level_border is not None:
            self._level_border = level_border

        self.account_level = identity.get('AccountLevel', self.account_level)
        self._incognito = identity.get('Incognito', self._incognito)
        self._hide_account_level = identity.get('HideAccountLevel', self._hide_account_level)

        if self == self._client.user:
            self.name = self._client.user.name
            self.tag = self._client.user.tag
            self.region = self._client.user.region

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

    def use_broadcast_hud(self) -> bool:
        """
        :class: `bool`
        Returns whether the player is using broadcast HUD.
        """
        return self._use_broadcast_hud

    def incognito(self) -> bool:
        """
        :class: `bool`
        Returns whether the player is incognito.
        """
        return self._incognito

    def hide_account_level(self) -> bool:
        """
        :class: `bool`
        Returns whether the player is hiding their account level.
        """
        return self._hide_account_level
