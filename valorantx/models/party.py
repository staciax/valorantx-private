from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..enums import QueueType, try_enum
from ..utils import MISSING
from .match import PlatformInfo

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from ..types.party import (
        CheatData as CheatDataPayload,
        CustomGameData as CustomGameDataPayload,
        CustomGameMembership as CustomGameMembershipPayload,
        CustomGameRules as CustomGameRulesPayload,
        CustomGameSettings as CustomGameSettingsPayload,
        Invite as InvitePayload,
        MatchmakingData as MatchmakingDataPayload,
        Member as MemberPayload,
        Party as PartyPayload,
        Ping as PingPayload,
        Player as PlayerPayload,
        PlayerIdentity as PlayerIdentityPayload,
        Request as RequestPayload,
    )
    from .competitive_tiers import Tier
    from .level_borders import LevelBorder
    from .player_cards import PlayerCard
    from .player_titles import PlayerTitle

__all__ = (
    'Party',
    'PartyMember',
    'PartyPlayer',
    'PlayerIdentity',
    'Ping',
    'CustomGameRules',
    'CustomGameSettings',
    'CustomGameMembership',
    'CustomGameData',
    'MatchmakingData',
    'CheatData',
)


class PartyPlayer:
    def __init__(self, *, client: Client, data: PlayerPayload) -> None:
        self._client = client
        self.subject: str = data['Subject']
        self.version: int = data['Version']
        self.current_party_id: str = data['CurrentPartyID']
        self.invites: Optional[Any] = data['Invites']
        self.requests: List[Any] = data['Requests']
        self.platform_info: PlatformInfo = PlatformInfo(data['PlatformInfo'])

    def __repr__(self) -> str:
        return f'<PartyPlayer subject={self.subject} version={self.version} current_party_id={self.current_party_id!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PartyPlayer) and other.subject == self.subject

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.subject)

    async def fetch_party(self) -> Party:
        return await self._client.fetch_party(self.current_party_id)

    def get_party(self) -> Party:
        party = Party(self._client, {'Version': 0})  # type: ignore
        party.id = self.current_party_id
        return party


class PlayerIdentity:
    def __init__(self, client: Client, data: PlayerIdentityPayload) -> None:
        self._client = client
        self.Subject: str = data['Subject']
        self.player_card_id: str = data['PlayerCardID']
        self.player_title_id: str = data['PlayerTitleID']
        self.account_level: int = data['AccountLevel']
        self.preferred_level_border_id: str = data['PreferredLevelBorderID']
        self.incognito: bool = data['Incognito']
        self.hide_account_level: bool = data['HideAccountLevel']

    @property
    def player_card(self) -> Optional[PlayerCard]:
        return self._client.valorant_api.get_player_card(self.player_card_id)

    @property
    def player_title(self) -> Optional[PlayerTitle]:
        return self._client.valorant_api.get_player_title(self.player_title_id)

    @property
    def level_border(self) -> Optional[LevelBorder]:
        return self._client.valorant_api.get_level_border(self.preferred_level_border_id)


class Ping:
    def __init__(self, data: PingPayload) -> None:
        self.ping: int = data['Ping']
        self.game_pod_id: str = data['GamePodID']

    @property
    def location(self) -> str:
        return self.game_pod_id.split('-')[-2]

    @property
    def region(self) -> str:
        return self.game_pod_id.split('-')[2].split('.')[1]


class PartyMember:
    def __init__(self, party: Party, data: MemberPayload) -> None:
        self._client = party._client
        self._party = party
        self._game_name: Optional[str] = None
        self._tag_line: Optional[str] = None
        self.subject: str = data['Subject']
        self._competitive_tier: int = data['CompetitiveTier']
        self.identity: PlayerIdentity = PlayerIdentity(self._client, data['PlayerIdentity'])
        self.seasonal_badge_info: Optional[Any] = data['SeasonalBadgeInfo']
        self._is_owner: bool = data.get('IsOwner', False)
        self.queue_eligible_remaining_account_levels: int = data['QueueEligibleRemainingAccountLevels']
        self.pings: List[Ping] = [Ping(ping) for ping in data['Pings']]
        self._is_ready: bool = data['IsReady']
        self._is_moderator: bool = data['IsModerator']
        self.use_broadcast_hud: bool = data['UseBroadcastHUD']
        self.platform_type: str = data['PlatformType']

    def __repr__(self) -> str:
        return f'<PartyMember subject={self.subject} game_name={self.game_name!r} tag_line={self.tag_line!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PartyMember) and other.subject == self.subject

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.subject)

    @property
    def id(self) -> str:
        return self.subject

    @property
    def competitive_tier(self) -> Optional[Tier]:
        season_act = self._client.act
        if season_act is MISSING:
            return None

        competitive_season = self._client.valorant_api.get_competitive_season_season_id(season_act.id)
        if competitive_season is None:
            return None

        if competitive_season.competitive_tiers is None:
            return None

        return competitive_season.competitive_tiers.get_tier(self._competitive_tier)

    @property
    def game_name(self) -> Optional[str]:
        return self._game_name

    @property
    def tag_line(self) -> Optional[str]:
        return self._tag_line

    def is_owner(self) -> bool:
        return self._is_owner

    def is_ready(self) -> bool:
        return self._is_ready

    def is_moderator(self) -> bool:
        return self._is_moderator

    def update_riot_id(self, game_name: Optional[str], tag_line: Optional[str]) -> None:
        if game_name is not None:
            self._game_name = game_name
        if tag_line is not None:
            self._tag_line = tag_line

    async def kick(self) -> None:
        await self._party.kick_member(self.id)


class CustomGameRules:
    def __init__(self, data: CustomGameRulesPayload) -> None:
        self.allow_game_modifiers: Optional[str] = data.get('AllowGameModifiers')
        self.is_overtime_win_by_two: Optional[str] = data.get('IsOvertimeWinByTwo')
        self.play_out_all_rounds: Optional[str] = data.get('PlayOutAllRounds')
        self.skip_match_history: Optional[str] = data.get('SkipMatchHistory')
        self.tournament_mode: Optional[str] = data.get('TournamentMode')


class CustomGameSettings:
    def __init__(self, data: CustomGameSettingsPayload) -> None:
        self.map: str = data['Map']
        self.mode: str = data['Mode']
        self.use_bots: bool = data['UseBots']
        self.game_pods: str = data['GamePod']
        self.game_rules: Optional[CustomGameRules] = None
        if data['GameRules'] is not None:
            self.game_rules = CustomGameRules(data['GameRules'])


class CustomGameMembership:
    def __init__(self, data: CustomGameMembershipPayload) -> None:
        self.team_one: Optional[Any] = data['teamOne']
        self.team_two: Optional[Any] = data['teamTwo']
        self.team_spectate: Optional[Any] = data['teamSpectate']
        self.team_one_coaches: Optional[Any] = data['teamOneCoaches']
        self.team_two_coaches: Optional[Any] = data['teamTwoCoaches']


class CustomGameData:
    def __init__(self, data: CustomGameDataPayload) -> None:
        self.settings: CustomGameSettings = CustomGameSettings(data['Settings'])
        self.membership: CustomGameMembership = CustomGameMembership(data['Membership'])
        self.max_party_size: int = data['MaxPartySize']
        self.autobalance_enabled: bool = data['AutobalanceEnabled']
        self.autobalance_min_players: int = data['AutobalanceMinPlayers']
        self.has_recovery_data: bool = data['HasRecoveryData']


class MatchmakingData:
    def __init__(self, data: MatchmakingDataPayload) -> None:
        self.queue_id: str = data['QueueID']
        self.queue: QueueType = try_enum(QueueType, data.get('QueueID'))
        self.preferred_game_pods: List[str] = data.get('PreferredGamePods')
        self.skill_disparity_rr_penalty: int = data.get('SkillDisparityRRPenalty')

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MatchmakingData) and other.queue_id == self.queue_id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Invite:
    def __init__(self, data: InvitePayload) -> None:
        self.id: str = data['ID']
        self.party_id: str = data['PartyID']
        self.subject: str = data['Subject']
        self.invited_by_subject: str = data['InvitedBySubject']
        self._created_at: str = data['CreatedAt']
        self._refreshed_at: str = data['RefreshedAt']
        self.expires_in: int = data['ExpiresIn']

    def __repr__(self) -> str:
        return f'<Invite id={self.id} party_id={self.party_id} subject={self.subject}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Invite) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    # @property
    # def created_at(self) -> datetime:
    #     # ISO 8601 format
    #     return datetime.fromisoformat(self._created_at)

    # @property
    # def refreshed_at(self) -> datetime:
    #     return datetime.fromisoformat(self._refreshed_at)


class Request:
    def __init__(self, client: Client, data: RequestPayload) -> None:
        self._client: Client = client
        self.id: str = data['ID']
        self.party_id: str = data['PartyID']
        self.requested_by_subject: str = data['RequestedBySubject']
        self.subjects: List[str] = data['Subjects']
        self._created_at: str = data['CreatedAt']
        self._refreshed_at: str = data['RefreshedAt']
        self.expires_in: int = data['ExpiresIn']

    def __repr__(self) -> str:
        return f'<Request id={self.id} party_id={self.party_id} requested_by_subject={self.requested_by_subject}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Request) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    async def decline(self) -> None:
        await self._client.http.post_party_decline_request(self.party_id, self.id)

    # @property
    # def created_at(self) -> datetime:
    #     # ISO 8601 format
    #     return datetime.fromisoformat(self._created_at)
    # @property
    # def refreshed_at(self) -> datetime:
    #     return datetime.fromisoformat(self._refreshed_at)


class CheatData:
    def __init__(self, data: CheatDataPayload) -> None:
        pass


class Party:
    def __init__(self, client: Client, data: PartyPayload) -> None:
        self._client: Client = client
        self._closed: bool = False
        self._members: Dict[str, PartyMember] = {}
        self._update(data)

    def _update(self, data: PartyPayload) -> None:
        if data['Version'] == 0:
            return
        self.id: str = data['ID']
        self.muc_name: str = data['MUCName']
        self.voice_room_id: str = data['VoiceRoomID']
        self.version: int = data['Version']
        self.client_version: str = data['ClientVersion']
        self.state: str = data['State']
        self.previous_state: str = data['PreviousState']
        self.state_transition_reason: str = data['StateTransitionReason']
        self.accessibility = data['Accessibility']
        self.custom_game_data: CustomGameData = CustomGameData(data['CustomGameData'])
        self.matchmaking_data: MatchmakingData = MatchmakingData(data['MatchmakingData'])
        self.invites: List[Invite] = []
        if data['Invites'] is not None:
            self.invites = [Invite(i) for i in data['Invites']]
        self.requests: List[Request] = []
        if data['Requests'] is not None:
            self.requests = [Request(self._client, r) for r in data['Requests']]
        self.queue_entry_time: str = data['QueueEntryTime']
        self.error_notification: str = data['ErrorNotification']
        self.restricted_seconds: int = data['RestrictedSeconds']
        self.eligible_queues: List[str] = data['EligibleQueues']
        self.queue_ineligibilities: Optional[List[Any]] = data['QueueIneligibilities']
        self.cheat_data = data['CheatData']
        self.xp_bonuses: Optional[List[Any]] = data['XPBonuses']
        self._closed: bool = self.accessibility == 'CLOSED'
        members: Dict[str, PartyMember] = {}
        if data['Members'] is not None:
            for m in data['Members']:
                member = PartyMember(self, m)
                if member_cache := self.get_member(member.id):
                    member.update_riot_id(member_cache.game_name, member_cache.tag_line)
                members[member.id] = member
        self._members: Dict[str, PartyMember] = members

    @property
    def members(self) -> List[PartyMember]:
        """List[:class:`PartyMember`]: A list of the party's members."""
        return list(self._members.values())

    def is_closed(self) -> bool:
        """:class:`bool`: Whether the party is closed."""
        return self._closed

    async def refresh(self) -> Self:
        """|coro|

        Refreshes the party data.
        """
        party = await self._client.http.get_party(party_id=self.id)
        self._update(party)
        # await self.update_member_display_name()
        return self

    def get_member(self, member_id: str) -> Optional[PartyMember]:
        """Returns a member from the party.

        Parameters
        ----------
        member_id: :class:`str`
            The member's ID.

        Returns
        -------
        Optional[:class:`PartyMember`]
            The member if found, else ``None``.
        """

        return self._members.get(member_id)

    async def invite_by_riot_id(self, game_name: str, tag_line: str, /) -> None:
        """|coro|
        Invite a player to the party by their Riot ID.

        Parameters
        ----------
        game_name: :class:`str`
            The player's game name.
        tag_line: :class:`str`
            The player's tag line.
        """
        data = await self._client.http.post_party_invite_by_display_name(party_id=self.id, name=game_name, tag=tag_line)
        self._update(data)

    async def remove_member(self, member: PartyMember, /) -> None:
        """|coro|

        Remove a player from the party.

        Parameters
        ----------
        member: :class:`PartyMember`
            The member to remove.
        """
        try:
            self._members.pop(member.id)
        except KeyError:
            pass

        await self._client.http.delete_party_remove_player(puuid=member.id)

    async def change_queue(self, queue_id: str, /) -> None:
        if queue_id not in self.eligible_queues:
            raise ValueError(f'Queue ID {queue_id} is not eligible for this party.')
        data = await self._client.http.post_party_queue(party_id=self.id, queue_id=queue_id)
        self._update(data)

    async def set_ready(self, ready: bool) -> None:
        data = await self._client.http.post_party_member_set_ready(self.id, ready)
        self._update(data)

    async def enter_matchmaking(self) -> None:
        """|coro|

        Join the matchmaking queue.
        """
        data = await self._client.http.post_party_matchmaking_join(party_id=self.id)
        self._update(data)

    async def leave_matchmaking(self) -> None:
        """|coro|

        Leave the matchmaking queue.
        """
        data = await self._client.http.post_party_matchmaking_leave(party_id=self.id)
        self._update(data)

    async def refresh_identity(self) -> None:
        """|coro|

        Refresh the identity of the party.
        """
        data = await self._client.http.post_party_refresh_player_identity(party_id=self.id)
        self._update(data)

    async def refresh_pings(self) -> None:
        """|coro|

        Refresh the identity of the party.
        """
        data = await self._client.http.post_party_refresh_pings(party_id=self.id)
        self._update(data)

    async def refresh_competitive_tier(self) -> None:
        data = await self._client.http.post_party_refresh_competitive_tier(self.id)
        self._update(data)

    async def kick_member(self, puuid: str, /) -> None:
        """|coro|

        Kick a member from the party.

        Parameters
        ----------
        member: :class:`PartyMember`
            The member to kick.

        Raises
        ------
        :exc:`HTTPException`
            Failed to kick the member.
        :exc:`Forbidden`
            You do not have permission to kick the member.
        """
        data = await self._client.http.delete_party_leave_from_party(party_id=self.id, puuid=puuid)
        self._update(data)

    async def transfer_owner(self, member: PartyMember, /) -> None:
        """|coro|

        Transfer the ownership of the party to a member.

        Parameters
        ----------
        member: :class:`PartyMember`
            The member to transfer ownership to.
        """
        data = await self._client.http.post_party_transfer_owner(party_id=self.id, puuid=member.id)
        self._update(data)

    async def refresh_member_riot_id(self) -> None:
        """|coro|

        Update the display name of members in the party.
        """
        if len(self.members) == 0:
            return
        puuids = [member.id for member in self.members if member.game_name is None or member.tag_line is None]
        name_service = await self._client.fetch_player_name_by_puuid(puuid=puuids)
        for name in name_service:
            member = self.get_member(name.subject)
            if member is not None:
                member.update_riot_id(name.game_name, name.tag_line)
