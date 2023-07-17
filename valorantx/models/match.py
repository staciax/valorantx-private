from __future__ import annotations

import asyncio
import contextlib
import datetime
import logging
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

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
        History as HistoryPayload,
        Location as LocationPayload,
        MatchDetails as MatchDetailsPayload,
        MatchHistory as MatchHistoryPayload,
        MatchInfo as MatchInfoPayload,
        NewPlayerExperienceDetails as NewPlayerExperienceDetailsPayload,
        PlatformInfo as PlatformInfoPayload,
        Player as PlayerPayload,
        PlayerLocation as PlayerLocationPayload,
        PlayerStats as PlayerStatsPayload,
        RoundDamage as RoundDamagePayload,
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
    from .competitive_tiers import Tier
    from .gamemodes import GameMode
    from .gear import Gear
    from .level_borders import LevelBorder
    from .maps import Map
    from .player_cards import PlayerCard
    from .player_titles import PlayerTitle
    from .seasons import Season
    from .weapons import Weapon

__all__ = (
    'AbilityCasts',
    'BehaviorFactors',
    'Coach',
    'Damage',
    'Economy',
    'FinishingDamage',
    'Kill',
    'Location',
    'MatchDetails',
    'MatchHistory',
    'MatchInfo',
    'MatchPlayer',
    'PlayerLocation',
    'NewPlayerExperienceDetails',
    'PlatformInfo',
    'PlayerStats',
    'RoundPlayerEconomy',
    'RoundPlayerScore',
    'RoundPlayerStat',
    'RoundResult',
    'Spike',
    'SpikeDefuse',
    'SpikePlant',
    'Team',
    'XPModification',
)

_log = logging.getLogger(__name__)


class MatchHistory:
    def __init__(self, client: Client, data: MatchHistoryPayload) -> None:
        self._client = client
        self.subject: str = data['Subject']
        self.total: int = data['Total']
        self.start_index: int = data['BeginIndex']
        self.end_index: int = data['EndIndex']
        self._history: List[HistoryPayload] = data['History']
        self._match_details: Dict[str, MatchDetails] = {}
        # self._client.loop.create_task(self._fetch_details())

    def __repr__(self) -> str:
        return f'<MatchHistory subject={self.subject!r} total={self.total!r}>'

    def __iter__(self) -> Iterator[MatchDetails]:
        return iter(list(self._match_details.values()))

    def __len__(self) -> int:
        return len(self._match_details)

    @property
    def match_details(self) -> List[MatchDetails]:
        """:class:`List[MatchDetails]`: Returns a list of :class:`MatchDetails`."""
        return list(self._match_details.values())

    # async def details(self) -> AsyncIterator[MatchDetails]:
    #     for match in self._history:
    #         match_details = await self._client.fetch_match_details(match['MatchID'])
    #         if match_details is not None:
    #             yield match_details

    async def fetch_details(self) -> None:
        """:class:`List[MatchDetails]`: Fetches the match details for each match in the history."""
        future_tasks = [asyncio.ensure_future(self._client.fetch_match_details(match['MatchID'])) for match in self._history]
        results = await asyncio.gather(*future_tasks)
        for match in results:
            self._match_details[match.id] = match


class MatchInfo:
    def __init__(self, client: Client, data: MatchInfoPayload) -> None:
        self._client = client
        self.match_id: str = data['matchId']
        self.map_id: str = data['mapId']
        self._map: Optional[Map] = self._client.valorant_api.get_map_by_url(data['mapId'])
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
        self._game_mode: Optional[GameMode] = self._client.valorant_api.get_game_mode_by_url(self._game_mode_url)
        self._is_ranked: bool = data['isRanked']
        self._is_match_sampled: bool = data['isMatchSampled']
        self.season_id: str = data['seasonId']
        self._season: Optional[Season] = self._client.valorant_api.get_season(self.season_id)
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
    def __init__(self, match: MatchDetails, data: CoachPayload) -> None:
        self._match: MatchDetails = match
        self.subject: str = data['subject']
        self.team_id: str = data['teamId']

    def __repr__(self) -> str:
        return f'<Coach subject={self.subject!r} team_id={self.team_id!r}>'

    @property
    def team(self) -> Optional[Team]:
        """:class:`Team`: coach's team"""
        return self._match.get_team(self.team_id)


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

    @property
    def members(self) -> List[MatchPlayer]:
        return [player for player in self._match.players if player.team == self]

    @property
    def opponents(self) -> List[MatchPlayer]:
        return [player for player in self._match.players if player.team != self]


class Party:
    def __init__(self, party_id: str, match: MatchDetails) -> None:
        self.id: str = party_id
        self.match: MatchDetails = match

    def __repr__(self) -> str:
        return f'<Party id={self.id!r}>'

    def __str__(self) -> str:
        return self.id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Party) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def members(self) -> List[MatchPlayer]:
        """:class:`List[MatchPlayer]`: Returns a list of all members in this party."""
        return [player for player in self.match.players if player.party == self]


class OpponentStats:
    def __init__(self, match: MatchDetails, player: MatchPlayer, player_opponent: MatchPlayer) -> None:
        self.match: MatchDetails = match
        self.player: MatchPlayer = player  # me (the player)
        self.opponent: MatchPlayer = player_opponent

        # player stats
        self.kills: int = 0
        self.assists: int = 0
        self.deaths: int = 0
        self.damages: int = 0
        self.head_shots: int = 0
        self.body_shots: int = 0
        self.leg_shots: int = 0

        # player opponent stats
        self.opponent_kills: int = 0
        self.opponent_assists: int = 0
        self.opponent_deaths: int = 0
        self.opponent_damages: int = 0
        self.opponent_head_shots: int = 0
        self.opponent_body_shots: int = 0
        self.opponent_leg_shots: int = 0

        self.__fill_stats()

    def __repr__(self) -> str:
        attrs = [
            ('opponent', self.opponent),
            ('kills', self.opponent_kills),
            ('assists', self.opponent_assists),
            ('deaths', self.opponent_deaths),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def kda_opponent(self) -> str:
        """:class:`str`: Returns the opponent's KDA."""
        return '{kills}/{deaths}/{assists}'.format(
            kills=self.opponent_kills, deaths=self.opponent_deaths, assists=self.opponent_assists
        )

    @property
    def kda(self) -> str:
        """:class:`str`: Returns the player's KDA."""
        return '{kills}/{deaths}/{assists}'.format(kills=self.kills, deaths=self.deaths, assists=self.assists)

    def __fill_stats(self) -> None:
        for kill in self.match.kills:
            if kill.killer == self.player and kill.victim == self.opponent:
                self.kills += 1
                self.opponent_deaths += 1

            if kill.killer == self.opponent and kill.victim == self.player:
                self.opponent_kills += 1
                self.deaths += 1

            if kill.killer is not None:
                if kill.killer.team != self.player.team:
                    if kill.victim == self.player:
                        for assist in kill.assistants:
                            if assist == self.opponent:
                                self.opponent_assists += 1

            else:
                if kill.victim == self.opponent:
                    for assist in kill.assistants:
                        if assist == self.player:
                            self.assists += 1

        for round_result in self.match.round_results:
            for stat in round_result.player_stats:
                if stat.player == self.player:
                    for dmg in stat.damage:
                        if dmg.receiver == self.opponent:
                            self.head_shots += dmg.head_shots
                            self.body_shots += dmg.body_shots
                            self.leg_shots += dmg.leg_shots
                            self.damages += dmg.damage

                if stat.player == self.opponent:
                    for dmg in stat.damage:
                        if dmg.receiver == self.player:
                            self.opponent_head_shots += dmg.head_shots
                            self.opponent_body_shots += dmg.body_shots
                            self.opponent_leg_shots += dmg.leg_shots
                            self.opponent_damages += dmg.damage


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
        self.site: str = data['plantSite']
        self.round_time: int = data.get('plantRoundTime', 0)
        self.location: Optional[Location] = None
        self.player_locations: List[PlayerLocation] = []
        plant_location = data.get('plantLocation')
        if plant_location:
            self.location: Optional[Location] = Location(plant_location)
        plant_player_locations = data.get('plantPlayerLocations')
        if plant_player_locations:
            self.player_locations: List[PlayerLocation] = [PlayerLocation(ppl) for ppl in plant_player_locations]
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
            ('player_locations', self.player_locations),
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
        self.player_locations: List[PlayerLocation] = []
        defuse_location = data.get('defuseLocation')
        if defuse_location:
            self.location: Optional[Location] = Location(defuse_location)
        defuse_player_locations = data.get('defusePlayerLocations')
        if defuse_player_locations:
            self.player_locations: List[PlayerLocation] = [PlayerLocation(x) for x in defuse_player_locations]
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
            ('player_locations', self.player_locations),
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
    def __init__(self, data: PlayerLocationPayload) -> None:
        self.subject: str = data['subject']
        self.view_radians: float = data['viewRadians']
        self.location: Location = Location(data['location'])

    def __repr__(self) -> str:
        return f"<PlayerLocation subject={self.subject!r} view_radians={self.view_radians!r} location={self.location!r}>"

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
        return self.match._client.valorant_api.get_weapon(self._item_uuid.lower())

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
        self.player_locations: List[PlayerLocation] = []
        if data['playerLocations'] is not None:
            self.player_locations = [PlayerLocation(location) for location in data['playerLocations']]
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

    def __repr__(self) -> str:
        attrs = [
            ('killer', self.killer),
            ('victim', self.victim),
            ('assistants', self.assistants),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

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
        return self.match._client.valorant_api.get_weapon(self._weapon.lower())

    @property
    def armor(self) -> Optional[Gear]:
        """:class:`Gear`: The armor used by the player."""
        if self._armor is None:
            return None
        return self.match._client.valorant_api.get_gear(self._armor.lower())


class RoundDamage:
    def __init__(self, match: MatchDetails, data: RoundDamagePayload) -> None:
        self.match: MatchDetails = match
        self._receiver_uuid: str = data.get('receiver')
        self.damage: int = data.get('damage', 0)
        self.round: int = data.get('round', 0)

    def __repr__(self) -> str:
        attrs = [
            ('receiver', self.receiver),
            ('damage', self.damage),
            ('round', self.round),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def receiver(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: The player who received the damage."""
        return self.match.get_player(self._receiver_uuid)


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
        self.player: Optional[MatchPlayer] = match.get_player(self.subject)

    def __repr__(self) -> str:
        attrs = [
            ('player', self.player),
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
            ('player', self.player),
            ('score', self.score),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __int__(self) -> int:
        return self.score

    @property
    def player(self) -> Optional[MatchPlayer]:
        """:class:`MatchPlayer`: Returns the player that this score belongs to."""
        return self._match.get_player(self.subject)


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
        self.player_economies: List[RoundPlayerEconomy] = []
        if data['playerEconomies'] is not None:
            self.player_economies = [RoundPlayerEconomy(match, player) for player in data['playerEconomies']]
        self.player_scores: List[RoundPlayerScore] = []
        if data['playerScores'] is not None:
            self.player_scores = [RoundPlayerScore(match, player) for player in data['playerScores']]
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

    @property
    def e(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the E ability."""
        return self.agent.get_ability(AbilityType.ability_2)

    @property
    def q(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the Q ability."""
        return self.agent.get_ability(AbilityType.ability_1)

    @property
    def c(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the C ability."""
        return self.agent.get_ability(AbilityType.grenade)

    @property
    def x(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the X ability."""
        return self.agent.get_ability(AbilityType.ultimate)

    @property
    def p(self) -> Optional[AgentAbility]:
        """:class:`AgentAbility`: Returns the passive ability."""
        return self.agent.get_ability(AbilityType.passive)


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
        if data.get('abilityCasts') is not None and self.agent is not None:
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


class MatchPlayer(User):  # Player
    def __init__(self, match: MatchDetails, data: PlayerPayload) -> None:
        super().__init__(match._client, data)
        self._match = match
        self.game_name = data['gameName']
        self.tag_line = data['tagLine']
        self.platform_info: PlatformInfo = PlatformInfo(data['platformInfo'])
        self.team_id: str = data['teamId']
        self.team: Optional[Team] = None
        self.party_id: str = data['partyId']
        self.party: Party = Party(data['partyId'], match)
        self._character_id = data['characterId']
        self.agent: Optional[Agent] = match._client.valorant_api.get_agent(self._character_id)
        self.stats: PlayerStats = PlayerStats(self.agent, data['stats'])
        self.round_damage: List[RoundDamage] = []
        if data['roundDamage'] is not None:
            self.round_damage = [RoundDamage(match, damage) for damage in data['roundDamage']]
        self.competitive_tier: Optional[Tier] = match._client.valorant_api.get_tier(
            season_id=match.match_info.season_id, tier=data['competitiveTier']
        )
        self._is_observer: bool = data['isObserver']
        self.player_card: Optional[PlayerCard] = match._client.valorant_api.get_player_card(data['playerCard'])
        self.player_title: Optional[PlayerTitle] = match._client.valorant_api.get_player_title(data['playerTitle'])
        self.preferred_level_border: Optional[LevelBorder] = match._client.valorant_api.get_level_border(
            data.get('preferredLevelBorder', None)
        )
        self.account_level: int = data['accountLevel']
        self.session_playtime_minutes: int = data.get('sessionPlaytimeMinutes', 0)
        self.xp_modifications: List[XPModification] = [XPModification(xp) for xp in data.get('xpModifications', [])]
        self.behavior_factors: BehaviorFactors = BehaviorFactors(data['behaviorFactors'])
        self.new_player_experience_details: NewPlayerExperienceDetails = NewPlayerExperienceDetails(
            data['newPlayerExperienceDetails']
        )
        self._is_winner: bool = False
        self.last_update: datetime.datetime = match.started_at

    def __repr__(self) -> str:
        return f'<PlayerMatch display_name={self.display_name!r} agent={self.agent!r} team={self.team!r}>'

    def init(self) -> None:
        self.team = self._match.get_team(self.team_id)
        self.stats._update()
        if self._match.winning_team is not None and self.team == self._match.winning_team:
            self._is_winner = True

    def is_winner(self) -> bool:
        """:class:`bool`: whether the player is on the winning team"""
        return self._is_winner

    def is_observer(self) -> bool:
        """:class:`bool`: whether the player is an observer"""
        return self._is_observer

    async def refresh_competitive_tier(self) -> None:
        mmr = await self._client.fetch_mmr(puuid=self.puuid)
        self.competitive_tier = mmr.get_latest_rank_tier()

    def get_opponents(self) -> List[MatchPlayer]:
        """:class:`list[MatchPlayer]`: list of opponents"""
        return [player for player in self._match.players if player.team != self.team]

    def get_opponents_stats(self) -> List[OpponentStats]:
        """:class:`Opponent` of the given player."""
        return [OpponentStats(self._match, self, opponent) for opponent in self.get_opponents()]


class MatchDetails:
    def __init__(self, client: Client, data: MatchDetailsPayload) -> None:
        self._client = client
        self.match_info: MatchInfo = MatchInfo(client, data['matchInfo'])
        self._players: Dict[str, MatchPlayer] = {player['subject']: MatchPlayer(self, player) for player in data['players']}
        self.bots: List[Any] = data['bots']
        self.coaches: Dict[str, Coach] = {coach['subject']: Coach(self, coach) for coach in data['coaches']}
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

    def __repr__(self) -> str:
        return f'<MatchDetails id={self.match_info.match_id!r} map={self.match_info.map!r} started_at={self.match_info.started_at!r} >'

    def _player_init(self) -> None:
        for player in self.players:
            player.init()

        # find mvp and team mvp

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

    # helpers

    def is_draw(self) -> bool:
        blue_team = self.get_team('Blue')
        red_team = self.get_team('Red')
        if blue_team is not None and red_team is not None:
            if blue_team.rounds_won == red_team.rounds_won:
                return True
        return False

    def get_members(self, player: MatchPlayer) -> List[MatchPlayer]:
        return [p for p in self.players if p.team_id == player.team_id]

    def get_opponents(self, player: MatchPlayer) -> List[MatchPlayer]:
        return [p for p in self.players if p.team_id != player.team_id]
