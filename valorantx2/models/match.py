from __future__ import annotations

# import asyncio
# import contextlib
# import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..client import Client
    from ..types.match import (
        Coach as CoachPayload,
        Economy as EconomyPayload,
        FinishingDamage as FinishingDamagePayload,
        Location as LocationPayload,
        MatchDetails as MatchDetailsPayload,
        MatchHistory as MatchHistoryPayload,
        MatchInfo as MatchInfoPayload,
        PlayerLocation as PlayerLocationPayload,
        RoundPlayerDamage as RoundPlayerDamagePayload,
        RoundPlayerEconomy as RoundPlayerEconomyPayload,
        RoundPlayerScore as RoundPlayerScorePayload,
        RoundPlayerStatKill as RoundPlayerStatKillPayload,
        RoundPlayerStats as RoundPlayerStatsPayload,
        RoundResult as RoundResultPayload,
        Team as TeamPayload,
    )
    from .gear import Gear

    # from .maps import Map
    from .weapons import Weapon


class History:
    def __init__(self, client: Client, data: MatchHistoryPayload) -> None:
        self._client = client
        self.subject: str = data['Subject']
        self.total: int = data['Total']
        self.start_index: int = data['BeginIndex']
        self.end_index: int = data['EndIndex']
        # self._history: List[MatchDetails] = []

    def __repr__(self) -> str:
        return f'<MatchHistory subject={self.subject!r} total={self.total!r}>'

    # def __iter__(self) -> Iterator[Details]:
    #     return iter(self._match_details)

    # def __len__(self) -> int:
    #     return len(self._match_details)

    # async def details(self) -> AsyncIterator[MatchDetails]:
    #     for match in self._history:
    #         match_id = match['MatchID']
    #         match_details = await self._client.fetch_match_details(match_id)
    #         if match_details is not None:
    #             yield match_details

    # async def fetch_details(self) -> List[Details]:
    #     """:class:`List[MatchDetails]`: Fetches the match details for each match in the history."""

    #     future_tasks = []
    #     for match in self._match_history:
    #         match_id = match['MatchID']
    #         # queue_id = match['QueueID']
    #         # start_time = match['GameStartTime']
    #         future_tasks.append(asyncio.ensure_future(self._client.fetch_match_details(match_id)))
    #     future_tasks = await asyncio.gather(*future_tasks)
    #     for future in future_tasks:
    #         self._match_details.append(future)

    #     return self._match_details

    # def get_match_details(self) -> List[Details]:
    #     """:class:`List[MatchDetails]`: Returns a list of :class:`MatchDetails`."""
    #     return self._match_details


# class Team:
#     def __init__(self, data: MatchTeamPayload, match: MatchDetails) -> None:
#         self.id: str = data.get('teamId')
#         self._is_won: bool = data.get('won', False)
#         self.round_played: int = data.get('roundsPlayed', 0)
#         self.rounds_won: int = data.get('roundsWon', 0)
#         self.number_points: int = data.get('numPoints', 0)
#         self._match: MatchDetails = match

#     def __repr__(self) -> str:
#         return f"<Team id={self.id!r} is_won={self.is_won()!r}>"

#     def __str__(self) -> str:
#         return self.id

#     def __bool__(self) -> bool:
#         return self.is_won()

#     def __eq__(self, other: object) -> bool:
#         return isinstance(other, Team) and self.id == other.id

#     def __ne__(self, other: object) -> bool:
#         return not self.__eq__(other)

#     def is_won(self) -> bool:
#         """:class:`bool`: Returns whether this team won the match."""
#         return self._is_won

#     def get_players(self) -> List[MatchPlayer]:
#         """:class:`List[MatchPlayer]`: Returns a list of players in this team."""
#         return [player for player in self._match.get_players() if player.team == self]


# class Location:
#     def __init__(self, data: MatchLocationPayload) -> None:
#         self.x: int = data.get('x', 0)
#         self.y: int = data.get('y', 0)

#     def __repr__(self) -> str:
#         return f'<Location x={self.x!r} y={self.y!r}>'

#     def __eq__(self, other: object) -> bool:
#         return isinstance(other, Location) and self.x == other.x and self.y == other.y

#     def __ne__(self, other: object) -> bool:
#         return not self.__eq__(other)


class MatchInfo:
    def __init__(self, client: Client, data: MatchInfoPayload) -> None:
        self._client = client
        self.match_id: str = data['matchId']
        self._map_id: str = data['mapId']  # TODO: map url to map id
        # self._map: Optional[Map] = self._client.valorant_api.get_map(self._map_id)
        self.gamePodId: str = data['gamePodId']
        self.game_loop_zone: str = data['gameLoopZone']
        self.game_server_address: str = data['gameServerAddress']
        self.game_version: str = data['gameVersion']
        self.game_length_millis: int = data['gameLengthMillis']
        self.game_start_millis: int = data['gameStartMillis']
        self.provisioning_flow_id: str = data['provisioningFlowID']
        self._is_completed: bool = data['isCompleted']
        self.custom_game_name: str = data['customGameName']
        self.force_post_processing: bool = data['forcePostProcessing']
        self.queue_id: str = data['queueID']
        self._game_mode: str = data['gameMode']
        self._is_ranked: bool = data['isRanked']
        self._is_match_sampled: bool = data['isMatchSampled']
        self._season_id: str = data['seasonId']
        self.completion_state: str = data['completionState']
        self.platform_type: str = data['platformType']
        self.premier_match_info: Any = data['premierMatchInfo']
        self.party_rr_penalties: Dict[str, float] = data['partyRRPenalties']
        self.should_match_disable_penalties: bool = data['shouldMatchDisablePenalties']

    def __repr__(self) -> str:
        return f'<MatchInfo match_id={self.match_id!r}>'

    def is_completed(self) -> bool:
        """:class:`bool`: Returns whether this match is completed."""
        return self._is_completed

    def is_ranked(self) -> bool:
        """:class:`bool`: Returns whether this match is ranked."""
        return self._is_ranked

    def is_match_sampled(self) -> bool:
        """:class:`bool`: Returns whether this match is sampled."""
        return self._is_match_sampled


class Coach:
    def __init__(self, data: CoachPayload) -> None:
        self.subject: str = data['subject']
        self.team_id: str = data['teamId']


class Team:
    def __init__(self, data: TeamPayload, match: MatchDetails) -> None:
        self.id: str = data['teamId']
        self._is_won: bool = data['won']
        self.round_played: int = data['roundsPlayed']
        self.rounds_won: int = data['roundsWon']
        self.number_points: int = data['numPoints']
        self._match: MatchDetails = match

    def __repr__(self) -> str:
        return f"<Team id={self.id!r} is_won={self._is_won!r}>"

    def __bool__(self) -> bool:
        return self._is_won

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Team) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def is_won(self) -> bool:
        return self._is_won

    # def get_players(self) -> List[MatchPlayer]:
    #     """:class:`List[MatchPlayer]`: Returns a list of players in this team."""
    #     return [player for player in self._match.get_players() if player.team == self]


class Location:
    def __init__(self, data: LocationPayload) -> None:
        self.x: int = data['x']
        self.y: int = data['y']

    def __repr__(self) -> str:
        return f'<Location x={self.x!r} y={self.y!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Location) and self.x == other.x and self.y == other.y

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class SpikePlant:
    def __init__(self, match: MatchDetails, data: RoundResultPayload) -> None:
        self.match: MatchDetails = match
        self._planter: Optional[str] = data.get('bombPlanter', None)
        self.site: str = data.get('plantSite', '')
        self.round_time: int = data.get('plantRoundTime', 0)
        self.location: Optional[Location] = None
        # self.player_locations: List[MatchPlayerLocation] = []
        plant_location = data.get('plantLocation')
        if plant_location:
            self.location: Optional[Location] = Location(plant_location)
        # plant_player_locations = data.get('plantPlayerLocations')
        # if plant_player_locations:
        #     self.player_locations: List[MatchPlayerLocation] = [MatchPlayerLocation(ppl) for ppl in plant_player_locations]

    def __repr__(self) -> str:
        attrs = [
            ('site', self.site),
            ('round_time', self.round_time),
            ('location', self.location),
            # ('player_locations', self.player_locations),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __str__(self) -> str:
        return self.site


#     def planter(self) -> Optional[MatchPlayer]:
#         """:class:`MatchPlayer`: Returns the player that planted the spike."""
#         return self.match.get_player(self._planter)


class SpikeDefuse:
    def __init__(self, match: MatchDetails, data: RoundResultPayload) -> None:
        self.match: MatchDetails = match
        self._defuser: Optional[str] = data.get('bombDefuser', None)
        self.round_time: int = data.get('defuseRoundTime', 0)
        self.location: Optional[Location] = None
        # self.player_locations: List[MatchPlayerLocation] = []
        defuse_location = data.get('defuseLocation')
        if defuse_location:
            self.location: Optional[Location] = Location(defuse_location)
        # defuse_player_locations = data.get('defusePlayerLocations')
        # if defuse_player_locations:
        #     self.player_locations: List[MatchPlayerLocation] = [MatchPlayerLocation(x) for x in defuse_player_locations]

    def __repr__(self) -> str:
        attrs = [
            ('round_time', self.round_time),
            ('location', self.location),
            # ('player_locations', self.player_locations),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    # def defuser(self) -> Optional[MatchPlayer]:
    #     """:class:`MatchPlayer`: Returns the player that defused the spike."""
    #     return self.match.get_player(self._defuser)


class Spike:
    def __init__(self, match: MatchDetails, data: RoundResultPayload) -> None:
        self.plant: Optional[SpikePlant] = None
        self.defuse: Optional[SpikeDefuse] = None
        if data.get('bombPlanter'):
            self.plant = SpikePlant(match, data)
        if data.get('bombPlanter'):
            self.defuse = SpikeDefuse(match, data)

    def __repr__(self) -> str:
        attrs = [
            ('plant', self.plant),
            ('defuse', self.defuse),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def is_planted(self) -> bool:
        """:class:`bool`: Returns whether the spike was planted in this round."""
        return self.plant is not None

    def is_defused(self) -> bool:
        """:class:`bool`: Returns whether the spike was defused in this round."""
        return self.defuse is not None

    # def plater(self) -> Optional[MatchPlayer]:
    #     """:class:`MatchPlayer`: Returns the player that planted the spike in this round."""
    #     return self.plant.planter() if self.plant else None

    # def defuser(self) -> Optional[MatchPlayer]:
    #     """:class:`MatchPlayer`: Returns the player that defused the spike in this round."""
    #     return self.defuse.defuser() if self.defuse else None


class PlayerLocation:
    # TODO: round_num
    def __init__(self, data: PlayerLocationPayload) -> None:
        self.subject: str = data['subject']
        self.view_radians: float = data['viewRadians']
        self.location: Location = Location(data['location'])

    def __repr__(self) -> str:
        return (
            f"<MatchPlayerLocation subject={self.subject!r} view_radians={self.view_radians!r} location={self.location!r}>"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PlayerLocation) and (
            self.subject == other.subject and self.view_radians == other.view_radians and self.location == other.location
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class FinishingDamage:
    def __init__(self, match: MatchDetails, data: FinishingDamagePayload) -> None:
        self.match: MatchDetails = match
        self.type: str = data.get('damageType')
        self._item_uuid: str = data.get('damageItem')
        self._is_secondary_fire_mode: bool = data.get('isSecondaryFireMode', False)

    def __repr__(self) -> str:
        attrs = [
            ('type', self.type),
            ('item', self.item),
            ('is_secondary_fire_mode', self.is_secondary_fire_mode),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FinishingDamage) and self.item == other.item

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def item(self) -> Optional[Any]:
        """:class:`Weapon` Returns the weapon used to kill the player."""
        return self.match._client.valorant_api.get_weapon(uuid=self._item_uuid.lower())

    def is_secondary_fire_mode(self) -> bool:
        """:class:`bool`: Whether the item was used in secondary fire mode."""
        return self._is_secondary_fire_mode


class Kill:
    def __init__(self, match: MatchDetails, data: RoundPlayerStatKillPayload) -> None:
        self.match: MatchDetails = match
        self.game_time: int = data['gameTime']
        self.round_time: int = data['roundTime']
        self._killer_uuid: str = data['killer']
        self._victim_uuid: str = data['victim']
        self.victim_location: Location = Location(data['victimLocation'])
        self._assistants: List[str] = data['assistants']
        # self.player_locations: List[PlayerLocation] = [
        #     PlayerLocation(location) for location in data['playerLocations']
        # ]
        self.finishing_damage: Optional[FinishingDamage] = (
            FinishingDamage(match, data['finishingDamage']) if data.get('finishingDamage') else None
        )

    # def __repr__(self) -> str:
    #     attrs = [
    #         ('killer', self.killer),
    #         ('victim', self.victim),
    #         ('assistants', self.assistants),
    #     ]
    #     joined = ' '.join('%s=%r' % t for t in attrs)
    #     return f'<{self.__class__.__name__} {joined}>'

    # @property
    # def killer(self) -> Optional[MatchPlayer]:
    #     """:class:`Optional[MatchPlayer]`: The player who killed the victim."""
    #     return self.match.get_player(self._killer_uuid)

    # @property
    # def victim(self) -> Optional[MatchPlayer]:
    #     """:class:`Optional[MatchPlayer]`: The player who was killed."""
    #     return self.match.get_player(self._victim_uuid)

    # @property
    # def assistants(self) -> List[MatchPlayer]:
    #     """:class:`List[MatchPlayer]`: The players who assisted in the kill."""
    #     players = []
    #     for uuid in self._assistants:
    #         player = self.match.get_player(uuid)
    #         if player is not None:
    #             players.append(player)
    #     return players


class Damage:
    def __init__(self, match: MatchDetails, data: RoundPlayerDamagePayload) -> None:
        self.match: MatchDetails = match
        self._receiver_uuid: str = data['receiver']
        self.damage: int = data['damage']
        self.head_shots: int = data['headshots']
        self.body_shots: int = data['bodyshots']
        self.leg_shots: int = data['legshots']

    # def __repr__(self) -> str:
    #     attrs = [
    #         ('receiver', self.receiver),
    #         ('damage', self.damage),
    #         ('head_shots', self.head_shots),
    #         ('body_shots', self.body_shots),
    #         ('leg_shots', self.leg_shots),
    #     ]
    #     joined = ' '.join('%s=%r' % t for t in attrs)
    #     return f'<{self.__class__.__name__} {joined}>'

    # @property
    # def receiver(self) -> Optional[MatchPlayer]:
    #     """:class:`MatchPlayer`: The player who received the damage."""
    #     return self.match.get_player(self._receiver_uuid)


class Economy:
    def __init__(self, match: MatchDetails, data: EconomyPayload) -> None:
        self.match: MatchDetails = match
        self.loadout_value: int = data.get('loadoutValue', 0)
        self._weapon: Optional[str] = data.get('weapon') if data.get('weapon') == '' else None
        self._armor: Optional[str] = data.get('armor') if data.get('armor') == '' else None
        self.remaining: int = data.get('remaining', 0)
        self.spent: int = data.get('spent', 0)

    def __repr__(self) -> str:
        attrs = [
            ('weapon', self.weapon),
            ('armor', self.armor),
            ('remaining', self.remaining),
            ('spent', self.spent),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Economy) and (
            self.loadout_value == other.loadout_value
            and self.weapon == other.weapon
            and self.armor == other.armor
            and self.remaining == other.remaining
            and self.spent == other.spent
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def weapon(self) -> Optional[Weapon]:
        """:class:`Weapon`: The weapon used by the player."""
        if self._weapon is None:
            return None
        return self.match._client.valorant_api.get_weapon(uuid=self._weapon.lower())

    @property
    def armor(self) -> Optional[Gear]:
        """:class:`Gear`: The armor used by the player."""
        if self._armor is None:
            return None
        return self.match._client.valorant_api.get_gear(uuid=self._armor.lower())


class PlayerStat:
    def __init__(self, match: MatchDetails, data: RoundPlayerStatsPayload) -> None:
        self._match: MatchDetails = match
        self.subject: str = data.get('subject')
        self.kills: List[Kill] = [Kill(match, kill) for kill in data['kills']]
        self.damage: List[Damage] = [Damage(match, damage) for damage in data.get('damage', [])]
        self.score: int = data.get('score', 0)
        self.economy: Economy = Economy(match, data.get('economy', {}))
        self.ability: Any = data['ability']
        self.was_afk: bool = data.get('wasAfk', False)
        self.was_penalized: bool = data.get('wasPenalized', False)
        self.stayed_in_spawn: bool = data.get('stayedInSpawn', False)

    # def __repr__(self) -> str:
    #     attrs = [
    #         ('player', self.player),
    #         ('kills', self.kills),
    #         ('score', self.score),
    #         ('economy', self.economy),
    #     ]
    #     joined = ' '.join('%s=%r' % t for t in attrs)
    #     return f'<{self.__class__.__name__} {joined}>'

    # @property
    # def player(self) -> Optional[MatchPlayer]:
    #     """:class:`MatchPlayer`: The player this stat belongs to."""
    #     return self.match.get_player(self.subject)


class PlayerEconomy(Economy):
    def __init__(self, match: MatchDetails, data: RoundPlayerEconomyPayload) -> None:
        super().__init__(match, data)
        self.subject: str = data['subject']
        # self.player: Optional[MatchPlayer] = match.get_player(self.subject)

    def __repr__(self) -> str:
        attrs = [
            # ('player', self.player),
            ('loadout_value', self.loadout_value),
            ('weapon', self.weapon),
            ('armor', self.armor),
            ('remaining', self.remaining),
            ('spent', self.spent),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PlayerEconomy) and (
            self.subject == other.subject
            and self.loadout_value == other.loadout_value
            and self.weapon == other.weapon
            and self.armor == other.armor
            and self.remaining == other.remaining
            and self.spent == other.spent
        )


class PlayerScore:
    def __init__(self, match: MatchDetails, data: RoundPlayerScorePayload) -> None:
        self._match: MatchDetails = match
        self.subject: str = data['subject']
        self.score: int = data['score']

    def __repr__(self) -> str:
        attrs = [
            # ('player', self.player),
            ('score', self.score),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __int__(self) -> int:
        return self.score

    # @property
    # def player(self) -> Optional[MatchPlayer]:
    #     """:class:`MatchPlayer`: Returns the player that this score belongs to."""
    #     return self.match.get_player(self.subject)


class RoundResult:
    def __init__(self, match: MatchDetails, data: RoundResultPayload) -> None:
        self._match = match
        self.round_number: int = data['roundNum']
        self.round_result: str = data['roundResult']
        self.round_ceremony: str = data['roundCeremony']
        self.winning_team: Optional[Team] = None
        self.spike: Spike = Spike(match, data)
        self.round_result_code: str = data['roundResultCode']
        self.player_stats: List[PlayerStat] = [PlayerStat(match, player) for player in data['playerStats']]
        self.player_economies: List[Any] = data['playerEconomies']
        self.player_scores: List[PlayerScore] = [PlayerScore(match, player) for player in data['playerScores']]

        # call later
        # for team in self._match.teams.values():
        #     if team.id == data['winningTeam']:
        #         self.winning_team = team

    def __int__(self) -> int:
        return self.round_number

    # def __bool__(self) -> bool:
    #     return self.match.me == self.winning_team

    # helper

    def spike_is_planted(self) -> bool:
        """:class:`bool`: Returns whether the spike was planted in this round."""
        return self.spike.is_planted()

    def spike_is_defused(self) -> bool:
        """:class:`bool`: Returns whether the spike was defused in this round."""
        return self.spike.is_defused()


class MatchDetails:
    def __init__(self, client: Client, data: MatchDetailsPayload) -> None:
        self._client = client
        self.match_info: MatchInfo = MatchInfo(client, data['matchInfo'])
        # self._players:Dict[str, MatchPlayer] = {player['subject']: MatchPlayer(player, self) for player in data['players']}
        self.bots: List[Any] = data['bots']
        self.coaches: Dict[str, Coach] = {coach['subject']: Coach(coach) for coach in data['coaches']}
        self.teams: Dict[str, Team] = {team['teamId']: Team(team, self) for team in data['teams']}
        self.round_results: List[RoundResult] = [RoundResult(self, round_result) for round_result in data['roundResults']]
        self.kills: List[Kill] = []
        for round_result in self.round_results:
            for player in round_result.player_stats:
                self.kills.extend(player.kills)
