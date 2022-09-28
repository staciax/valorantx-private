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

import asyncio
import contextlib
import datetime
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

from .. import utils
from ..enums import LevelBorderID, MapID, QueueID, RoundResultCode, RoundResultType, try_enum
from .player import BasePlayer

if TYPE_CHECKING:
    from ..client import Client
    from ..types.match import (
        Economy as EconomyPayload,
        FinishingDamage as FinishingDamagePayload,
        Location as MatchLocationPayload,
        MatchDetails as MatchDetailsPayload,
        MatchHistory as MatchHistoryPayload,
        MatchHistoryList as MatchHistoryListPayload,
        MatchKill as MatchKillPayload,
        MatchRoundPlayerStats as MatchRoundPlayerStatsPayload,
        MatchRoundResult as MatchRoundResultPayload,
        NewPlayerExperienceDetails as NewPlayerExperienceDetailsPayload,
        PlayerDamage as PlayerDamagePayload,
        PlayerEconomy as PlayerEconomyPayload,
        PlayerLocation as PlayerLocationPayload,
        PlayerScore as PlayerScorePayload,
        PlayerStatKill as PlayerStatKillPayload,
        RoundDamage as RoundDamagePayload,
        Team as MatchTeamPayload,
        XpModification as xpModificationPayload,
    )
    from ..types.player import PlayerMatch as PlayerMatchPayload
    from .agent import Agent
    from .gear import Gear
    from .map import Map
    from .weapons import Weapon

__all__ = (
    'MatchHistory',
    'MatchDetails',
    'MatchPlayer',
)


class MatchHistory:
    def __init__(self, client: Client, data: MatchHistoryPayload) -> None:
        self.uuid: str = data.get('Subject')
        self._client = client
        self.total_matches: int = data.get('Total', 0)
        self._match_history: List[MatchHistoryListPayload] = data.get('History', [])
        self._start: int = data.get('BeginIndex', 0)
        self._end: int = data.get('EndIndex', 0)
        self.match_details: List[MatchDetails] = []

    def __repr__(self) -> str:
        return f"<MatchHistory total_matches={self.total_matches!r} match_details={self.match_details!r}>"

    def __iter__(self) -> Iterator[MatchDetails]:
        return iter(self.match_details)

    def __len__(self) -> int:
        return len(self.match_details)

    async def fetch_history(self) -> List[MatchDetails]:

        future_tasks = []
        for match in self._match_history:
            match_id = match['MatchID']
            # queue_id = match['QueueID']
            # start_time = match['GameStartTime']
            future_tasks.append(asyncio.ensure_future(self._client.fetch_match_details(match_id)))
        future_tasks = await asyncio.gather(*future_tasks)
        for future in future_tasks:
            self.match_details.append(future)

        return self.match_details


class Team:
    def __init__(self, data: MatchTeamPayload) -> None:
        self.id: str = data.get('teamId')
        self._is_won: bool = data.get('won', False)
        self.round_played: int = data.get('roundsPlayed', 0)
        self.rounds_won: int = data.get('roundsWon', 0)
        self.number_points: int = data.get('numPoints', 0)

    def is_won(self) -> bool:
        return self._is_won

    def __repr__(self) -> str:
        return f"<Team id={self.id!r} is_won={self.is_won()!r}>"

    def __str__(self) -> str:
        return self.id

    def __bool__(self) -> bool:
        return self.is_won()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MatchDetails) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Location:
    def __init__(self, data: MatchLocationPayload):
        self.x: int = data.get('x', 0)
        self.y: int = data.get('y', 0)

    def __repr__(self) -> str:
        return f"<Location x={self.x!r} y={self.y!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Location) and self.x == other.x and self.y == other.y

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Economy:
    def __init__(self, match: MatchDetails, data: EconomyPayload):
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
        return isinstance(other, PlayerEconomy) and (
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
        if self._weapon is None:
            return None
        return self.match._client.get_weapon(uuid=self._weapon.lower())

    @property
    def armor(self) -> Optional[Gear]:
        if self._armor is None:
            return None
        return self.match._client.get_gear(uuid=self._armor.lower())


class PlayerEconomy(Economy):
    def __init__(self, match: MatchDetails, data: PlayerEconomyPayload):
        super().__init__(match, data)
        self.subject: str = data.get('subject')
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
        return isinstance(other, PlayerEconomy) and (
            self.subject == other.subject
            and self.loadout_value == other.loadout_value
            and self.weapon == other.weapon
            and self.armor == other.armor
            and self.remaining == other.remaining
            and self.spent == other.spent
        )


class MatchPlayerLocation:
    def __init__(self, data: PlayerLocationPayload) -> None:
        self.subject: str = data.get('subject')
        self.view_radians: float = data.get('viewRadians', 0.0)
        self.location: Location = Location(data.get('location', {}))

    def __repr__(self) -> str:
        return (
            f"<MatchPlayerLocation subject={self.subject!r} view_radians={self.view_radians!r} location={self.location!r}>"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MatchPlayerLocation) and (
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
        return self.match._client.get_weapon(uuid=self._item_uuid.lower())

    def is_secondary_fire_mode(self) -> bool:
        return self._is_secondary_fire_mode


class Kill:
    def __init__(self, match: MatchDetails, data: PlayerStatKillPayload) -> None:
        self.match: MatchDetails = match
        self.game_time: int = data.get('gameTime', 0)
        self.round_time: int = data.get('roundTime', 0)
        self._killer_uuid: str = data.get('killer')
        self._victim_uuid: str = data.get('victim')
        self.victim_location: Location = Location(data.get('victimLocation', {}))
        self._assistants: List[str] = data.get('assistants', [])
        self.player_locations: List[MatchPlayerLocation] = [
            MatchPlayerLocation(location) for location in data.get('playerLocations', [])
        ]
        self.finishing_damage: Optional[FinishingDamage] = (
            FinishingDamage(match, data['finishingDamage']) if data.get('finishingDamage') else None
        )

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
        return self.match.get_player(self._killer_uuid)

    @property
    def victim(self) -> Optional[MatchPlayer]:
        return self.match.get_player(self._victim_uuid)

    @property
    def assistants(self) -> List[MatchPlayer]:
        return [self.match.get_player(uuid) for uuid in self._assistants]


class Damage:
    def __init__(self, match: MatchDetails, data: PlayerDamagePayload) -> None:
        self.match: MatchDetails = match
        self._receiver_uuid: str = data.get('receiver')
        self.damage: int = data.get('damage', 0)
        self.headshots: int = data.get('headshots', 0)
        self.bodyshots: int = data.get('bodyshots', 0)
        self.legshots: int = data.get('legshots', 0)

    def __repr__(self) -> str:
        attrs = [
            ('receiver', self.receiver),
            ('damage', self.damage),
            ('headshots', self.headshots),
            ('bodyshots', self.bodyshots),
            ('legshots', self.legshots),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def receiver(self) -> Optional[MatchPlayer]:
        return self.match.get_player(self._receiver_uuid)


class PlayerStat:
    def __init__(self, match: MatchDetails, data: MatchRoundPlayerStatsPayload) -> None:
        self.match: MatchDetails = match
        self.subject: str = data.get('subject')
        self.kills: List[Kill] = [Kill(match, kill) for kill in data.get('kills', [])]
        self.damage: List[Damage] = [Damage(match, damage) for damage in data.get('damage', [])]
        self.score: int = data.get('score', 0)
        self.economy: Economy = Economy(match, data.get('economy', {}))
        self.__ability: Dict[str, Any] = data.get('ability', {})  # TODO: Implement ability
        self._was_afk: bool = data.get('wasAfk', False)
        self._was_penalized: bool = data.get('wasPenalized', False)
        self._stayed_in_spawn: bool = data.get('stayedInSpawn', False)

    def __repr__(self) -> str:
        attrs = [
            ('player', self.player),
            ('kills', self.kills),
            ('score', self.score),
            ('economy', self.economy),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def player(self) -> Optional[MatchPlayer]:
        """Returns the player that this stat belongs to."""
        return self.match.get_player(self.subject)

    def was_afk(self) -> bool:
        return self._was_afk

    def was_penalized(self) -> bool:
        return self._was_penalized

    def stayed_in_spawn(self) -> bool:
        return self._stayed_in_spawn


class playerScore:
    def __init__(self, match: MatchDetails, data: PlayerScorePayload) -> None:
        self.match: MatchDetails = match
        self.subject: str = data.get('subject')
        self.score: int = data.get('score', 0)

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
        """Returns the player that this stat belongs to."""
        return self.match.get_player(self.subject)


class SpikePlant:
    def __init__(self, data: MatchRoundResultPayload) -> None:
        self.site: str = data.get('plantSite', None)
        self.round_time: int = data.get('plantRoundTime', 0)
        self.location: Optional[Location] = Location(data['plantLocation']) if data.get('plantLocation') else None
        self.player_locations: List[MatchPlayerLocation] = (
            [MatchPlayerLocation(x) for x in data['plantPlayerLocations']] if data.get('plantPlayerLocations') else []
        )

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


class SpikeDefuse:
    def __init__(self, data: MatchRoundResultPayload) -> None:
        self.round_time: int = data.get('defuseRoundTime', 0)
        self.location: Optional[Location] = Location(data['defuseLocation']) if data.get('defuseLocation') else None
        self.player_locations: List[MatchPlayerLocation] = (
            [MatchPlayerLocation(x) for x in data['defusePlayerLocations']] if data.get('defusePlayerLocations') else []
        )

    def __repr__(self) -> str:
        attrs = [
            ('round_time', self.round_time),
            ('location', self.location),
            ('player_locations', self.player_locations),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'


class RoundResult:
    def __init__(self, match: MatchDetails, data: MatchRoundResultPayload) -> None:
        self.match: MatchDetails = match
        self.round_number: int = data.get('roundNum', 0)
        self.result: RoundResultType = try_enum(RoundResultType, data.get('roundResult'))
        self._winning_team: str = data.get('winningTeam')
        self.plant: Optional[SpikePlant] = SpikePlant(data) if data.get('plantSite') != '' else None
        self.defuse: Optional[SpikeDefuse] = SpikeDefuse(data) if data.get('defuseRoundTime') != 0 else None
        self.result_code: RoundResultCode = try_enum(RoundResultCode, data.get('roundResultCode', ''))
        self.ceremony: Optional[str] = data.get('roundCeremony', None)  # TODO: Implement ceremony
        self.player_economies: List[PlayerEconomy] = (
            [PlayerEconomy(match, economy) for economy in data['playerEconomies']] if data.get('playerEconomies') else []
        )
        self.player_stats: List[PlayerStat] = [PlayerStat(match, player) for player in data.get('playerStats', [])]
        self.player_scores: List[playerScore] = [playerScore(match, player) for player in data.get('playerScores', [])]

    def __int__(self) -> int:
        return self.round_number

    def __bool__(self) -> bool:
        return self.match.me == self.winning_team

    def winning_team(self) -> Optional[Team]:
        for team in self.match.teams:
            if team.id == self._winning_team:
                return team
        return None


class Platform:
    def __init__(self, data: Dict[str, str]):
        self.type: str = data['platformType']
        self.os: str = data['platformOS']
        self.os_version: str = data['platformOSVersion']
        self.chipset: str = data['platformChipset']

    def __repr__(self) -> str:
        return f'<Platform type={self.type!r} os={self.os!r} os_version={self.os_version!r} chipset={self.chipset!r}>'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Platform)
            and other.type == self.type
            and other.os == self.os
            and other.os_version == self.os_version
            # and other.chipset == self.chipset
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class MatchPlayer(BasePlayer):

    # https://github.com/staciax/reinabot/blob/master/cogs/valorant/embeds.py

    def __init__(self, *, client: Client, data: PlayerMatchPayload, match_details: MatchDetails) -> None:
        super().__init__(client=client, data=data)
        self.match_details = match_details
        self._character_id: str = data['characterId']
        self._team_id: str = data['teamId']
        self.party_id: str = data['partyId']
        self._is_winner: bool = False
        self.play_time_seconds: float = data['stats']['playtimeMillis'] / 1000
        self.account_level: int = data['accountLevel']
        self._player_card_id: str = data['playerCard']
        self._player_title_id: str = data['playerCard']
        self._level_border_id: str = data.get('preferredLevelBorder', str(LevelBorderID._1))
        self._competitive_rank: int = data['competitiveTier']
        self.platform: Platform = Platform(data['platformInfo'])

        # stats
        self.round_damage: List[RoundDamagePayload] = data['roundDamage']
        self.score: int = 0
        self.kills: int = 0
        self.deaths: int = 0
        self.assists: int = 0
        self.rounds_played: int = 0
        self.first_blood: int = 0
        self.first_death: int = 0
        self.plants: int = 0
        self.defuses: int = 0
        self.damages: int = 0
        self.head_shots: int = 0
        self.body_shots: int = 0
        self.leg_shots: int = 0
        self.headshot_percent: float = 0
        self.body_shot_percent: float = 0
        self.leg_shot_percent: float = 0
        self.clutchs: int = 0

        # behavior
        self.afk_rounds: int = data['behaviorFactors']['afkRounds']
        self.collisions: float = data['behaviorFactors']['collisions']
        self.damage_participation_out_going: int = data['behaviorFactors']['damageParticipationOutgoing']
        self.friendly_fire_in_coming: int = data['behaviorFactors']['friendlyFireIncoming']
        self.friendly_fire_out_going: int = data['behaviorFactors']['friendlyFireOutgoing']
        self.mouse_movement: int = data['behaviorFactors']['mouseMovement']
        self.stayed_in_spawn_rounds: int = data['behaviorFactors']['stayedInSpawnRounds']

        # other info
        self.session_playtime_minutes: int = data.get('sessionPlaytimeMinutes', 0)
        self.xpModifications: List[xpModificationPayload] = data.get('xpModifications', [])

        # new player
        self.new_player_exp_details: NewPlayerExperienceDetailsPayload = data['newPlayerExperienceDetails']

        self.__fill_match_data()

    def __repr__(self) -> str:
        return f'<PlayerMatch uuid={self.puuid!r} name={self.name!r} tagline={self.tagline!r} region={self.region!r}>'

    def __fill_match_data(self) -> None:

        for round_result in self.match_details.round_results:
            death_on_round = []
            for stat in round_result.player_stats:
                for kill in stat.kills:
                    death_on_round.append(kill)

                if stat.player == self:
                    for dmg in stat.damage:
                        self.head_shots += dmg.headshots
                        self.body_shots += dmg.bodyshots
                        self.leg_shots += dmg.legshots

            if len(death_on_round) > 0:
                first_blood = sorted(death_on_round, key=lambda x: x.round_time)[0]
                if first_blood.killer == self:
                    self.first_blood += 1

                if first_blood.victim == self:
                    self.first_death += 1

        with contextlib.suppress(ZeroDivisionError):
            hs_percent, bs_percent, ls_percent = utils.percent(self.head_shots, self.body_shots, self.leg_shots)
            self.headshot_percent, self.bodyshot_percent, self.legshot_percent = hs_percent, bs_percent, ls_percent

    def is_winner(self) -> bool:
        return self._is_winner

    @property
    def team(self) -> Optional[Team]:
        for team in self.match_details.teams:
            if team.id == self._team_id:
                return team
        return None

    @property
    def team_blue(self) -> Optional[Team]:
        for team in self.match_details.teams:
            if team.id == 'Blue':
                return team
        return None

    @property
    def team_red(self) -> Optional[Team]:
        for team in self.match_details.teams:
            if team.id == 'Red':
                return team
        return None

    @property
    def agent(self) -> Agent:
        """player's agent"""
        return self._client.get_agent(uuid=self._character_id)

    @property
    def character(self) -> Agent:
        """player's character"""
        return self.agent

    @property
    def party_members(self) -> List[Optional[MatchPlayer]]:
        return [
            MatchPlayer(client=self._client, data=player, match_details=self.match_details)
            for player in self.match_details.players
            if player.party_id == self.party_id and player.puuid != self.puuid
        ]

    def ability_casts(self) -> None:
        """in designer"""
        return None

    @property
    def average_combat_score(self):
        with contextlib.suppress(ZeroDivisionError):
            return self.score / self.rounds_played
        return 0

    @property
    def kd_ratio(self) -> float:
        with contextlib.suppress(ZeroDivisionError):
            return self.kills / self.deaths
        return 0

    @property
    def kda_ratio(self) -> float:
        with contextlib.suppress(ZeroDivisionError):
            return self.kills / self.deaths / self.assists
        return 0

    @property
    def damage_per_round(self) -> float:
        with contextlib.suppress(ZeroDivisionError):
            return self.damages / self.rounds_played
        return 0

    # alias
    @property
    def acs(self):
        """alias for average_combat_score"""
        return self.average_combat_score


class MatchDetails:
    def __init__(self, client: Client, data: MatchDetailsPayload) -> None:
        self._client = client
        self._match_info = match_info = data['matchInfo']
        self.id: str = match_info.get('matchId')
        self._map_url: str = match_info.get('mapId')
        self._queue_id: QueueID = try_enum(QueueID, match_info.get('queueID'))
        self._is_ranked: bool = match_info.get('isRanked', False)
        self._is_match_sampled: bool = match_info.get('isMatchSampled')
        self._season_id: str = match_info.get('seasonId')
        self._game_version: str = match_info.get('gameVersion')

        self._coaches: List[Dict[str, Any]] = data['coaches']
        self._bots: List[Dict[str, Any]] = data['bots']
        self._kills: List[MatchKillPayload] = data['kills']
        self._round_results: List[MatchRoundResultPayload] = data['roundResults']
        self._teams: List[MatchTeamPayload] = data['teams']

        self._completion_state: str = match_info.get('completionState')
        self._game_pod_id: str = match_info.get('gamePodId')
        self._game_loop_zone: str = match_info.get('gameLoopZone')
        self._platform_type: str = match_info.get('platformType')
        self._should_match_disable_penalties: bool = match_info.get('shouldMatchDisablePenalties')
        self._provisioning_FlowID: str = match_info.get('provisioningFlowID')
        self._game_start_millis: int = match_info.get('gameStartMillis')
        self._players: List[Dict[str, Any]] = data['players']
        self._game_length: int = match_info.get('gameLengthMillis')
        self._is_won: bool = False

    def __repr__(self) -> str:
        attrs = [
            ('id', self.id),
            ('queue', self.queue),
            ('started_at', self.started_at.strftime('%Y-%m-%d %H:%M:%S')),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MatchDetails) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        return self.is_won()

    @property
    def user(self) -> Any:
        return self._client.user

    def is_won(self) -> bool:
        return self._is_won

    def is_ranked(self) -> bool:
        return self._is_ranked

    @property
    def map(self) -> Map:
        to_uuid = MapID.from_url(self._map_url)
        return self._client.get_map(uuid=to_uuid)

    @property
    def started_at(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self._game_start_millis / 1000)

    @property
    def game_length(self) -> int:
        """Returns the length of the game in seconds"""
        return self._game_length // 1000

    @property
    def queue(self) -> QueueID:
        return self._queue_id

    @property
    def players(self) -> Optional[List[MatchPlayer]]:
        return [MatchPlayer(client=self._client, data=player, match_details=self) for player in self._players]

    @property
    def bots(self) -> List[Any]:
        """:class:`List[Any]`: Returns a list of bots in the match"""
        return self._bots

    @property
    def teams(self) -> List[Team]:
        """:class:`List[Any]`: Returns a list of teams in the match"""
        return [Team(data=team) for team in self._teams]

    @property
    def coaches(self) -> List[Any]:
        """:class:`List[Any]`: Returns a list of coaches in the match"""
        return self._coaches

    @property
    def round_results(self) -> List[RoundResult]:
        """:class:`List[RoundResult]`: Returns a list of round results in the match"""
        return [RoundResult(match=self, data=round_result) for round_result in self._round_results]

    @property
    def kills(self) -> List[Dict[str, Any]]:
        """:class:`List[Dict[str, Any]]`: Returns a list of kills in the match"""
        return self._kills

    @property
    def me(self) -> Optional[MatchPlayer]:
        """Returns the :class:`MatchPlayer` object for the current user"""
        for player in self.players:
            if player.puuid == self._client.user.puuid:
                return player
        return None

    def get_player(self, uuid: str) -> Optional[MatchPlayer]:
        """Returns the :class:`MatchPlayer` object for the given uuid"""
        for player in self.players:
            if player.puuid == uuid:
                return player
        return None


class MatchContract(MatchDetails):
    __slot__ = ('xp_grants', 'reward_grants', 'mission_deltas', 'contract_deltas', 'could_progress_missions')

    def __init__(self, client: Client, data: Any) -> None:
        super().__init__(client, data)
        self.xp_grants: Any = data.get('XPGrants', None)
        self.reward_grants: Any = data.get('RewardGrants', None)
        self.mission_deltas: Any = data.get('MissionDeltas', None)
        self.contract_deltas: Any = data.get('ContractDeltas', None)
        self._could_progress_missions: bool = data.get('CouldProgressMissions', False)

    def __repr__(self) -> str:
        attrs = [
            ('id', self.id),
            ('queue', self.queue),
            ('started_at', self.started_at.strftime('%Y-%m-%d %H:%M:%S')),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def could_progress_missions(self) -> bool:
        return self._could_progress_missions
