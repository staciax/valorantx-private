from __future__ import annotations

# import asyncio
import contextlib
import datetime
import logging

# import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .. import utils
from ..enums import AbilityType
from .user import User

if TYPE_CHECKING:
    from ..client import Client
    from ..types.match import (
        AbilityCasts as AbilityCastsPayload,
        BehaviorFactors as BehaviorFactorsPayload,
        Coach as CoachPayload,
        Economy as EconomyPayload,
        FinishingDamage as FinishingDamagePayload,
        Location as LocationPayload,
        MatchDetails as MatchDetailsPayload,
        MatchHistory as MatchHistoryPayload,
        MatchInfo as MatchInfoPayload,
        NewPlayerExperienceDetails as NewPlayerExperienceDetailsPayload,
        PlatformInfo as PlatformInfoPayload,
        Player as PlayerPayload,
        PlayerLocation as PlayerLocationPayload,
        PlayerStats as PlayerStatsPayload,
        RoundPlayerDamage as RoundPlayerDamagePayload,
        RoundPlayerEconomy as RoundPlayerEconomyPayload,
        RoundPlayerScore as RoundPlayerScorePayload,
        RoundPlayerStatKill as RoundPlayerStatKillPayload,
        RoundPlayerStats as RoundPlayerStatsPayload,
        RoundResult as RoundResultPayload,
        Team as TeamPayload,
        XPModification as XPModificationPayload,
    )
    from .agents import Ability as AgentAbility, Agent
    from .gamemodes import GameMode
    from .gear import Gear
    from .level_borders import LevelBorder
    from .maps import Map
    from .player_cards import PlayerCard
    from .player_titles import PlayerTitle
    from .seasons import Season
    from .weapons import Weapon

_log = logging.getLogger(__name__)


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
        self._map: Optional[Map] = self._client.valorant_api.get_map(self._map_id)
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
        self._game_mode_url: str = data['gameMode']
        self._game_mode: Optional[GameMode] = self._client.valorant_api.get_game_mode(self._game_mode_url)
        self._is_ranked: bool = data['isRanked']
        self._is_match_sampled: bool = data['isMatchSampled']
        self._season_id: str = data['seasonId']
        self._season: Optional[Season] = self._client.valorant_api.get_season(uuid=self._season_id)
        self.completion_state: str = data['completionState']
        self.platform_type: str = data['platformType']
        self.premier_match_info: Any = data['premierMatchInfo']
        self.party_rr_penalties: Dict[str, float] = data['partyRRPenalties']
        self.should_match_disable_penalties: bool = data['shouldMatchDisablePenalties']
        self._is_surrendered: bool = False

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

    def is_surrendered(self) -> bool:
        """:class:`bool`: Whether the user surrendered this match."""
        return self._is_surrendered

    # property

    @property
    def map(self) -> Optional[Map]:
        """:class:`Map`: The map this match was played on."""
        return self._map

    @property
    def game_mode(self) -> Optional[GameMode]:
        """:class:`GameMode`: The game mode this match was played in."""
        return self._game_mode

    @property
    def started_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The time this match started."""
        return datetime.datetime.fromtimestamp(self.game_start_millis / 1000)

    @property
    def game_length(self) -> int:
        """:class:`int`: The length of this match in seconds."""
        return self.game_length // 1000

    @property
    def season(self) -> Optional[Season]:
        """:class:`Season`: Returns the season this match was played in."""
        return self._season


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

    def get_players(self) -> List[MatchPlayer]:
        return [player for player in self._match.players if player.team == self]


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
        self._planter_id: Optional[str] = data.get('bombPlanter', None)
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
        self._planter: Optional[MatchPlayer] = None
        if self._planter_id:
            self._planter = self.match.get_player(self._planter_id)
            if self._planter is not None:
                self._planter.stats.plants += 1
            else:
                _log.warning(f'Could not find planter with id {self._planter_id} in match {self.match.id}')

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

    @property
    def planter(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: Returns the player that planted the spike."""
        return self._planter


class SpikeDefuse:
    def __init__(self, match: MatchDetails, data: RoundResultPayload) -> None:
        self.match: MatchDetails = match
        self._defuser_id: Optional[str] = data.get('bombDefuser', None)
        self.round_time: int = data.get('defuseRoundTime', 0)
        self.location: Optional[Location] = None
        # self.player_locations: List[MatchPlayerLocation] = []
        defuse_location = data.get('defuseLocation')
        if defuse_location:
            self.location: Optional[Location] = Location(defuse_location)
        # defuse_player_locations = data.get('defusePlayerLocations')
        # if defuse_player_locations:
        #     self.player_locations: List[MatchPlayerLocation] = [MatchPlayerLocation(x) for x in defuse_player_locations]
        self._defuser: Optional[MatchPlayer] = None
        if self._defuser_id:
            self._defuser = self.match.get_player(self._defuser_id)
            if self._defuser is not None:
                self._defuser.stats.defuses += 1
            else:
                _log.warning(f'could not find defuser {self._defuser_id} in match {self.match.id}')

    def __repr__(self) -> str:
        attrs = [
            ('round_time', self.round_time),
            ('location', self.location),
            # ('player_locations', self.player_locations),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def defuser(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: Returns the player that defused the spike."""
        return self._defuser


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

    # helpers

    def is_planted(self) -> bool:
        """:class:`bool`: Returns whether the spike was planted in this round."""
        return self.plant is not None

    def is_defused(self) -> bool:
        """:class:`bool`: Returns whether the spike was defused in this round."""
        return self.defuse is not None

    @property
    def plater(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: Returns the player that planted the spike in this round."""
        if self.plant is None:
            return None
        return self.plant.planter

    @property
    def defuser(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: Returns the player that defused the spike in this round."""
        if self.defuse is None:
            return None
        return self.defuse.defuser


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
        self._assistants_list: List[str] = data['assistants']
        # self.player_locations: List[PlayerLocation] = [
        #     PlayerLocation(location) for location in data['playerLocations']
        # ]
        self.finishing_damage: Optional[FinishingDamage] = (
            FinishingDamage(match, data['finishingDamage']) if data.get('finishingDamage') else None
        )
        self._killer: Optional[MatchPlayer] = self.match.get_player(self._killer_uuid)
        self._victim: Optional[MatchPlayer] = self.match.get_player(self._victim_uuid)
        self._assistants: List[MatchPlayer] = []
        for uuid in self._assistants_list:
            player = self.match.get_player(uuid)
            if player is not None:
                self._assistants.append(player)

    # def __repr__(self) -> str:
    #     attrs = [
    #         ('killer', self.killer),
    #         ('victim', self.victim),
    #         ('assistants', self.assistants),
    #     ]
    #     joined = ' '.join('%s=%r' % t for t in attrs)
    #     return f'<{self.__class__.__name__} {joined}>'

    @property
    def killer(self) -> Optional[MatchPlayer]:
        """:class:`Optional[MatchPlayer]`: The player who killed the victim."""
        return self._killer

    @property
    def victim(self) -> Optional[MatchPlayer]:
        """:class:`Optional[MatchPlayer]`: The player who was killed."""
        return self._victim

    @property
    def assistants(self) -> List[MatchPlayer]:
        """:class:`List[MatchPlayer]`: The players who assisted in the kill."""
        return self._assistants


class Damage:
    def __init__(self, match: MatchDetails, data: RoundPlayerDamagePayload) -> None:
        self.match: MatchDetails = match
        self._receiver_uuid: str = data['receiver']
        self.damage: int = data['damage']
        self.head_shots: int = data['headshots']
        self.body_shots: int = data['bodyshots']
        self.leg_shots: int = data['legshots']
        self._receiver: Optional[MatchPlayer] = self.match.get_player(self._receiver_uuid)

    def __repr__(self) -> str:
        attrs = [
            ('receiver', self.receiver),
            ('damage', self.damage),
            ('head_shots', self.head_shots),
            ('body_shots', self.body_shots),
            ('leg_shots', self.leg_shots),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def receiver(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: The player who received the damage."""
        return self._receiver


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


class RoundPlayerStat:
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
        self.__update_player_stats()

    def __repr__(self) -> str:
        attrs = [
            ('player', self.player),
            ('kills', self.kills),
            ('score', self.score),
            ('economy', self.economy),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __update_player_stats(self) -> None:
        if self.player is None:
            _log.warning(f'Player {self.subject} not found in match {self._match.id}')
            return

        stats = self.player.stats

        # for kill in sorted(self.kills, key=lambda x: x.round_time):
        #     if kill.killer == self.player:
        #         stats.first_kills += 1
        #     if kill.victim == self.player:
        #         stats.first_deaths += 1
        #     break

        for dmg in self.damage:
            stats.head_shots += dmg.head_shots
            stats.body_shots += dmg.body_shots
            stats.leg_shots += dmg.leg_shots
            stats.damages += dmg.damage

        # kills
        if len(self.kills) > 3:
            stats.multi_kills += 1

        if len(self.kills) == 5:
            stats.ace += 1

        # score
        # self.score += stat.score

        # behavior
        if self.was_afk:
            stats.afk_time += 1

        if self.was_penalized:
            stats.penalized_time += 1

        if self.stayed_in_spawn:
            stats.stayed_in_spawn += 1

    @property
    def player(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: The player this stat belongs to."""
        return self._match.get_player(self.subject)


class RoundPlayerEconomy(Economy):
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
        return isinstance(other, RoundPlayerEconomy) and (
            self.subject == other.subject
            and self.loadout_value == other.loadout_value
            and self.weapon == other.weapon
            and self.armor == other.armor
            and self.remaining == other.remaining
            and self.spent == other.spent
        )


class RoundPlayerScore:
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
        self.player_stats: List[RoundPlayerStat] = [RoundPlayerStat(match, player) for player in data['playerStats']]
        self.player_economies: List[RoundPlayerEconomy] = [
            RoundPlayerEconomy(match, player) for player in data['playerEconomies']
        ]
        self.player_scores: List[RoundPlayerScore] = [RoundPlayerScore(match, player) for player in data['playerScores']]
        for team in self._match.teams:
            if team.id == data['winningTeam']:
                self.winning_team = team
        self._update()

    def __int__(self) -> int:
        return self.round_number

    # def __bool__(self) -> bool:
    #     return self.match.me == self.winning_team

    def _update(self) -> None:
        if self.round_result_code.lower() == 'surrendered':
            self._match.match_info._is_surrendered = True

        kills: List[Kill] = []
        for stat in self.player_stats:
            for kill in sorted(stat.kills, key=lambda x: x.round_time):
                kills.append(kill)

        for kill in sorted(kills, key=lambda x: x.round_time):
            if kill.killer is not None:
                kill.killer.stats.first_kills += 1
            if kill.victim is not None:
                kill.victim.stats.first_deaths += 1
            break

    # helper

    def spike_is_planted(self) -> bool:
        """:class:`bool`: Returns whether the spike was planted in this round."""
        return self.spike.is_planted()

    def spike_is_defused(self) -> bool:
        """:class:`bool`: Returns whether the spike was defused in this round."""
        return self.spike.is_defused()


class BehaviorFactors:
    def __init__(self, data: BehaviorFactorsPayload) -> None:
        pass


class NewPlayerExperienceDetails:
    def __init__(self, data: NewPlayerExperienceDetailsPayload) -> None:
        pass


class XPModification:
    def __init__(self, data: XPModificationPayload) -> None:
        self.value: float = data['Value']
        self.id: str = data['ID']


class PlatformInfo:
    def __init__(self, data: PlatformInfoPayload) -> None:
        self.type: str = data['platformType']
        self.os: str = data['platformOS']
        self.os_version: str = data['platformOSVersion']
        self.chipset: str = data['platformChipset']

    def __repr__(self) -> str:
        return f'<Platform type={self.type!r} os={self.os!r} os_version={self.os_version!r}>'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PlatformInfo)
            and other.type == self.type
            and other.os == self.os
            and other.os_version == self.os_version
            and other.chipset == self.chipset
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class AbilityCasts:
    def __init__(self, agent: Agent, data: AbilityCastsPayload) -> None:
        self.agent: Agent = agent
        self._grenade_casts: int = data['grenadeCasts']
        self._ability1_casts: int = data['ability1Casts']
        self._ability2_casts: int = data['ability2Casts']
        self._ultimate_casts: int = data['ultimateCasts']

    def __repr__(self) -> str:
        attrs = [
            ('e_casts', self.e_casts),
            ('q_casts', self.q_casts),
            ('c_casts', self.c_casts),
            ('x_casts', self.x_casts),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def e_casts(self) -> int:
        """:class:`int`: Returns the number of E ability casts."""
        return self._ability2_casts

    @property
    def q_casts(self) -> int:
        """:class:`int`: Returns the number of Q ability casts."""
        return self._ability1_casts

    @property
    def c_casts(self) -> int:
        """:class:`int`: Returns the number of C ability casts."""
        return self._grenade_casts

    @property
    def x_casts(self) -> int:
        """:class:`int`: Returns the number of X ability casts."""
        return self._ultimate_casts

    def get_ability(self, slot: AbilityType) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the ability for the given slot."""
        for skill in self.agent.abilities:
            if skill.slot == slot:
                return skill

    @property
    def e(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the E ability."""
        return self.get_ability(AbilityType.ability_2)

    @property
    def q(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the Q ability."""
        return self.get_ability(AbilityType.ability_1)

    @property
    def c(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the C ability."""
        return self.get_ability(AbilityType.grenade)

    @property
    def x(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the X ability."""
        return self.get_ability(AbilityType.ultimate)

    @property
    def p(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the passive ability."""
        return self.get_ability(AbilityType.passive)


class PlayerStats:
    def __init__(self, agent: Optional[Agent], data: PlayerStatsPayload) -> None:
        self.agent: Optional[Agent] = agent
        self.score: int = data['score']
        self.rounds_played: int = data['roundsPlayed']
        self.kills: int = data['kills']
        self.deaths: int = data['deaths']
        self.assists: int = data['assists']
        self.playtime_millis: int = data['playtimeMillis']
        self.ability_casts: Optional[AbilityCasts] = None
        if data.get('abilityCasts') and self.agent:
            self.ability_casts = AbilityCasts(self.agent, data['abilityCasts'])
        self.first_kills: int = 0
        self.first_deaths: int = 0
        self.plants: int = 0
        self.defuses: int = 0
        self.damages: int = 0
        self.head_shots: int = 0
        self.body_shots: int = 0
        self.leg_shots: int = 0

        # self.clutches: int = 0  # TODO: implement

        self.multi_kills: int = 0  # kill more than 3 enemies in a round
        self.ace: int = 0  # kill all enemies in a round

        # self.weapon_stats: Dict[str, Any] = {}

        # percent
        self.head_shot_percent: float = 0
        self.body_shot_percent: float = 0
        self.leg_shot_percent: float = 0

        # behavior
        self.afk_time: int = 0
        self.penalized_time: int = 0
        self.stayed_in_spawn: int = 0

    def _update(self) -> None:
        with contextlib.suppress(ZeroDivisionError):
            self.head_shot_percent, self.body_shot_percent, self.leg_shot_percent = utils.percent(
                self.head_shots, self.body_shots, self.leg_shots
            )

    @property
    def average_combat_score(self) -> float:
        """:class:`float` average combat score"""
        with contextlib.suppress(ZeroDivisionError):
            return self.score / self.rounds_played
        return 0

    @property
    def kd_ratio(self) -> float:
        """:class:`float`: kill/death ratio"""
        with contextlib.suppress(ZeroDivisionError):
            return self.kills / self.deaths
        return 0

    @property
    def kda_ratio(self) -> float:
        """:class:`float`: KDA ratio"""
        with contextlib.suppress(ZeroDivisionError):
            return self.kills / self.deaths / self.assists
        return 0

    @property
    def damage_per_round(self) -> float:
        """:class:`float`: average damage per round"""
        with contextlib.suppress(ZeroDivisionError):
            return self.damages / self.rounds_played
        return 0

    @property
    def kda(self) -> str:
        """:class:`str`: kills/deaths/assists"""
        return f'{self.kills}/{self.deaths}/{self.assists}'

    @property
    def acs(self) -> float:
        """:class:`str`: average combat score"""
        return self.average_combat_score

    # def get_competitive_rank(self) -> Optional[Tier]:
    #     """:class:`Tier`: player's competitive rank"""
    #     season = self.match.get_season()
    #     return self._client.get_tier(self._competitive_rank, season)

    # async def fetch_competitive_rank(self) -> Optional[Tier]:
    #     """|coro|

    #     Fetch player's competitive rank

    #     Returns
    #     -------
    #     Optional[:class:`Tier`]
    #         player's competitive rank
    #     """
    #     tier = self.get_competitive_rank()
    #     if tier is not None:
    #         return tier
    #     season = self.match.get_season()
    #     mmr = await self._client.fetch_mmr(puuid=self.puuid)
    #     return mmr.get_latest_rank_tier(season_act=season)


class MatchPlayer(User):  # Player
    def __init__(self, match: MatchDetails, data: PlayerPayload) -> None:
        super().__init__(match._client, data)
        self._match = match
        self.game_name = data['gameName']
        self.tag_line = data['tagLine']
        self.platform_info: PlatformInfo = PlatformInfo(data['platformInfo'])
        self._team_id: str = data['teamId']
        self.team: Optional[Team] = None
        self.party_id: str = data['partyId']
        self._character_id = data['characterId']
        self.agent: Optional[Agent] = match._client.valorant_api.get_agent(uuid=self._character_id)
        self.stats: PlayerStats = PlayerStats(self.agent, data['stats'])
        # self.round_damage
        # self.competitive_tier
        self._is_observer: bool = data['isObserver']
        self.player_card: Optional[PlayerCard] = match._client.valorant_api.get_player_card(uuid=data['playerCard'])
        self.player_title: Optional[PlayerTitle] = match._client.valorant_api.get_player_title(uuid=data['playerTitle'])
        self.level_border: Optional[LevelBorder] = match._client.valorant_api.get_level_border(
            uuid=data.get('preferredLevelBorder', None)
        )
        self.account_level: int = data['accountLevel']
        self.session_playtime_minutes: int = data['sessionPlaytimeMinutes']
        self.xp_modifications: List[XPModification] = [XPModification(xp) for xp in data.get('xpModifications', [])]
        self.behavior_factors: BehaviorFactors = BehaviorFactors(data['behaviorFactors'])
        self.new_player_experience_details: NewPlayerExperienceDetails = NewPlayerExperienceDetails(
            data['newPlayerExperienceDetails']
        )
        self._is_winner: bool = False

    def init(self) -> None:
        self.team = self._match.get_team(self._team_id)
        self.stats._update()
        if self._match.winning_team is not None and self.team == self._match.winning_team:
            self._is_winner = True

    def is_winner(self) -> bool:
        """:class:`bool`: whether the player is on the winning team"""
        return self._is_winner


#         self.party: Party = Party(data, match)
#         self.party_id: str = data['partyId']
#         self.play_time_seconds: float = data['stats']['playtimeMillis'] / 1000

#         self._competitive_rank: int = data['competitiveTier']
#         self.platform: Platform = Platform(data['platformInfo'])
#         self._round_damage: Optional[List[RoundDamagePayload]] = data.get('roundDamage') or []

#         self.last_update = match.started_at

#     def __repr__(self) -> str:
#         return f'<PlayerMatch display_name={self.display_name!r} agent={self.agent!r} team={self.team!r}>'

#     def get_opponent(self, player_opponent: MatchPlayer) -> Opponent:
#         """:class:`Opponent` of the given player."""
#         if player_opponent.team == self.team:
#             raise ValueError('Player Opponent is your teammate')
#         return Opponent(self.match, self, player_opponent)

#     def is_winner(self) -> bool:
#         """:class:`bool`: Returns True if the player won the match."""
#         return self._is_winner

#     @property
#     def team(self) -> Optional[Team]:
#         """:class:`Team`: The team the player is on."""
#         return self.match.get_team(self._team_id)

#     @property
#     def agent(self) -> Optional[Agent]:
#         """:class:`Agent`: The agent of the player."""
#         return self._client.get_agent(uuid=self._character_id)

#     @property
#     def character(self) -> Optional[Agent]:
#         """:class:`Agent` alias"""
#         return self.agent

#     @property
#     def round_damage(self) -> Optional[List[RoundDamage]]:
#         """:class:`List[RoundDamage]`: list of round damage"""
#         if self._round_damage is not None:
#             return [RoundDamage(self.match, data) for data in self._round_damage]

#     def get_party_members(self) -> List[Optional[MatchPlayer]]:
#         """:class:`MatchPlayer` of party members"""
#         return [player for player in self.match._players if player.party_id == self.party_id and player.puuid != self.puuid]

#     @property
#     def average_combat_score(self) -> float:
#         """:class:`float` average combat score"""
#         with contextlib.suppress(ZeroDivisionError):
#             return self.score / self.rounds_played
#         return 0

#     def get_competitive_rank(self) -> Optional[Tier]:
#         """:class:`Tier`: player's competitive rank"""
#         season = self.match.get_season()
#         return self._client.get_tier(self._competitive_rank, season)

#     async def fetch_competitive_rank(self) -> Optional[Tier]:
#         """|coro|

#         Fetch player's competitive rank

#         Returns
#         -------
#         Optional[:class:`Tier`]
#             player's competitive rank
#         """
#         tier = self.get_competitive_rank()
#         if tier is not None:
#             return tier
#         season = self.match.get_season()
#         mmr = await self._client.fetch_mmr(puuid=self.puuid)
#         return mmr.get_latest_rank_tier(season_act=season)


class MatchDetails:
    def __init__(self, client: Client, data: MatchDetailsPayload) -> None:
        self._client = client
        self.match_info: MatchInfo = MatchInfo(client, data['matchInfo'])
        self._players: Dict[str, MatchPlayer] = {player['subject']: MatchPlayer(self, player) for player in data['players']}
        self.bots: List[Any] = data['bots']
        self.coaches: Dict[str, Coach] = {coach['subject']: Coach(coach) for coach in data['coaches']}
        self._teams: Dict[str, Team] = {team['teamId']: Team(team, self) for team in data['teams']}
        self.round_results: List[RoundResult] = [RoundResult(self, round_result) for round_result in data['roundResults']]
        self.kills: List[Kill] = []
        for round_result in self.round_results:
            for player in round_result.player_stats:
                self.kills.extend(player.kills)
        self.winning_team: Optional[Team] = None  # Union[Team, MatchPlayer]
        for team in self.teams:
            if team.is_won():
                self.winning_team = team
                break
        self._player_mvp: Optional[MatchPlayer] = None
        self._player_team_mvp: Optional[MatchPlayer] = None

        self._player_init()

    def _player_init(self) -> None:
        for player in self.players:
            player.init()

        player_max_acs = max(self.players, key=lambda p: p.stats.acs)
        player_2nd_max_acs = max([p for p in self.players if p.team != player_max_acs.team], key=lambda p: p.stats.acs)

        if player_max_acs.is_winner():
            self._player_mvp = player_max_acs
            self._player_team_mvp = player_2nd_max_acs
        else:
            self._player_mvp = player_2nd_max_acs
            self._player_team_mvp = player_max_acs

    # properties

    @property
    def started_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The time this match started."""
        return datetime.datetime.fromtimestamp(self.match_info.game_start_millis / 1000)

    # players

    @property
    def players(self) -> List[MatchPlayer]:
        """:class:`MatchPlayer` list"""
        return list(self._players.values())

    def get_player(self, puuid: str) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer` of the given puuid."""
        return self._players.get(puuid)

    def get_players_by_team(self, team: Team) -> List[MatchPlayer]:
        """:class:`List[MatchPlayer]`: Returns a list of enemy players in this match."""
        return [player for player in self.players if player.team == team]

    # teams

    @property
    def teams(self) -> List[Team]:
        """:class:`Team` list"""
        return list(self._teams.values())

    def get_team(self, team_id: str) -> Optional[Team]:  # Literal['red', 'blue']
        """:class:`Team` of the given team id."""
        return self._teams.get(team_id)

    # helpers

    @property
    def id(self) -> str:
        """:class:`str`: match id"""
        return self.match_info.match_id

    @property
    def match_mvp(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: Returns the match mvp."""
        return self._player_mvp

    @property
    def team_mvp(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: Returns the team mvp."""
        return self._player_team_mvp
