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
from ..enums import AbilityType, GameModeID, MapID, QueueID, RoundResultCode, RoundResultType, try_enum
from .player import Player

if TYPE_CHECKING:
    from ..client import Client
    from ..types.match import (  # MatchKill as MatchKillPayload,
        AbilityCasts as AbilityCastsPayload,
        Coach as CoachPayload,
        Economy as EconomyPayload,
        FinishingDamage as FinishingDamagePayload,
        Location as MatchLocationPayload,
        MatchDetails as MatchDetailsPayload,
        MatchHistory as MatchHistoryPayload,
        MatchHistoryList as MatchHistoryListPayload,
        MatchRoundPlayerStats as MatchRoundPlayerStatsPayload,
        MatchRoundResult as MatchRoundResultPayload,
        NewPlayerExperienceDetails as NewPlayerExperienceDetailsPayload,
        PlayerDamage as PlayerDamagePayload,
        PlayerEconomy as PlayerEconomyPayload,
        PlayerLocation as PlayerLocationPayload,
        PlayerMatch as PlayerMatchPayload,
        PlayerScore as PlayerScorePayload,
        PlayerStatKill as PlayerStatKillPayload,
        RoundDamage as RoundDamagePayload,
        Team as MatchTeamPayload,
        XpModification as xpModificationPayload,
    )
    from .agent import Agent, AgentAbility  # noqa
    from .competitive import Tier
    from .gamemode import GameMode
    from .gear import Gear
    from .level_border import LevelBorder
    from .map import Map
    from .player_card import PlayerCard
    from .player_title import PlayerTitle
    from .season import Season
    from .weapons import Weapon

__all__ = ('MatchDetails', 'MatchHistory', 'MatchPlayer', 'Platform')


class MatchHistory:
    def __init__(self, client: Client, data: MatchHistoryPayload) -> None:
        self.uuid: str = data.get('Subject')
        self._client = client
        self.total_matches: int = data.get('Total', 0)
        self._match_history: List[MatchHistoryListPayload] = data.get('History', [])
        self._start: int = data.get('BeginIndex', 0)
        self._end: int = data.get('EndIndex', 0)
        self._match_details: List[MatchDetails] = []

    def __repr__(self) -> str:
        return f"<MatchHistory total_matches={self.total_matches!r} match_details={self._match_details!r}>"

    def __iter__(self) -> Iterator[MatchDetails]:
        return iter(self._match_details)

    def __len__(self) -> int:
        return len(self._match_details)

    async def fetch_details(self) -> List[MatchDetails]:

        future_tasks = []
        for match in self._match_history:
            match_id = match['MatchID']
            # queue_id = match['QueueID']
            # start_time = match['GameStartTime']
            future_tasks.append(asyncio.ensure_future(self._client.fetch_match_details(match_id)))
        future_tasks = await asyncio.gather(*future_tasks)
        for future in future_tasks:
            self._match_details.append(future)

        return self._match_details

    def get_match_details(self) -> List[MatchDetails]:
        return self._match_details


class Team:
    def __init__(self, data: MatchTeamPayload, match: MatchDetails) -> None:
        self.id: str = data.get('teamId')
        self._is_won: bool = data.get('won', False)
        self.round_played: int = data.get('roundsPlayed', 0)
        self.rounds_won: int = data.get('roundsWon', 0)
        self.number_points: int = data.get('numPoints', 0)
        self._match: MatchDetails = match

    def is_won(self) -> bool:
        return self._is_won

    def __repr__(self) -> str:
        return f"<Team id={self.id!r} is_won={self.is_won()!r}>"

    def __str__(self) -> str:
        return self.id

    def __bool__(self) -> bool:
        return self.is_won()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Team) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def get_players(self) -> List[MatchPlayer]:
        return [player for player in self._match._players if player.team == self]


class Location:
    def __init__(self, data: MatchLocationPayload):
        self.x: int = data.get('x', 0)
        self.y: int = data.get('y', 0)

    def __repr__(self) -> str:
        return f'<Location x={self.x!r} y={self.y!r}>'

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
        self.head_shots: int = data.get('headshots', 0)
        self.body_shots: int = data.get('bodyshots', 0)
        self.leg_shots: int = data.get('legshots', 0)

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
        return self.match.get_player(self._receiver_uuid)


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


class PlayerScore:
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
    def __init__(self, match: MatchDetails, data: MatchRoundResultPayload) -> None:
        self.match: MatchDetails = match
        self._planter: Optional[str] = data.get('bombPlanter', None)
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

    def planter(self) -> Optional[MatchPlayer]:
        return self.match.get_player(self._planter)


class SpikeDefuse:
    def __init__(self, match: MatchDetails, data: MatchRoundResultPayload) -> None:
        self.match: MatchDetails = match
        self._defuser: Optional[str] = data.get('bombDefuser', None)
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

    def defuser(self) -> Optional[MatchPlayer]:
        return self.match.get_player(self._defuser)


class Spike:
    def __init__(self, match: MatchDetails, data: MatchRoundResultPayload) -> None:
        self.plant: SpikePlant = SpikePlant(match, data) if data.get('bombPlanter') is not None else None
        self.defuse: SpikeDefuse = SpikeDefuse(match, data) if data.get('bombDefuser') is not None else None

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

    def plater(self) -> Optional[MatchPlayer]:
        return self.plant.planter() if self.plant else None

    def defuser(self) -> Optional[MatchPlayer]:
        return self.defuse.defuser() if self.defuse else None


class RoundResult:
    def __init__(self, match: MatchDetails, data: MatchRoundResultPayload) -> None:
        self.match: MatchDetails = match
        self.round_number: int = data.get('roundNum', 0)
        self.result: RoundResultType = try_enum(RoundResultType, data.get('roundResult'))
        self._winning_team: str = data.get('winningTeam')
        self.spike: Spike = Spike(match, data)
        self.result_code: RoundResultCode = try_enum(RoundResultCode, data.get('roundResultCode'))
        self.ceremony: Optional[str] = data.get('roundCeremony', None)  # TODO: Implement ceremony
        self.player_economies: List[PlayerEconomy] = (
            [PlayerEconomy(match, economy) for economy in data['playerEconomies']] if data.get('playerEconomies') else []
        )
        self.player_stats: List[PlayerStat] = [PlayerStat(match, player) for player in data.get('playerStats', [])]
        self.player_scores: List[PlayerScore] = (
            [PlayerScore(match, player) for player in data['playerScores']] if data.get('playerScores') else []
        )
        if self.result_code == RoundResultCode.surrendered:
            self.match._is_surrendered = True

    def __int__(self) -> int:
        return self.round_number

    def __bool__(self) -> bool:
        return self.match.me == self.winning_team

    def winning_team(self) -> Optional[Team]:
        for team in self.match.teams:
            if team.id == self._winning_team:
                return team
        return None

    def spike_is_planted(self) -> bool:
        return self.spike.is_planted()

    def spike_is_defused(self) -> bool:
        return self.spike.is_defused()


class Platform:
    def __init__(self, data: Dict[str, str]):
        self.type: str = data['platformType']
        self.os: str = data['platformOS']
        self.os_version: str = data['platformOSVersion']
        self.chipset: str = data['platformChipset']

    def __repr__(self) -> str:
        return f'<Platform type={self.type!r} os={self.os!r} os_version={self.os_version!r}>'

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


class Party:
    def __init__(self, data: PlayerMatchPayload, match: MatchDetails):
        self.match: MatchDetails = match
        self.id: str = data['partyId']

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

    def get_members(self) -> List[MatchPlayer]:
        return [player for player in self.match._players if player.party == self]


class Opponent:
    def __init__(self, match: MatchDetails, player: MatchPlayer, player_opponent: MatchPlayer):
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
        return '{kills}/{deaths}/{assists}'.format(
            kills=self.opponent_kills, deaths=self.opponent_deaths, assists=self.opponent_assists
        )

    def __fill_stats(self) -> None:
        for kill in self.match.kills:

            if kill.killer == self.player and kill.victim == self.opponent:
                self.kills += 1
                self.opponent_deaths += 1

            if kill.killer == self.opponent and kill.victim == self.player:
                self.opponent_kills += 1
                self.deaths += 1

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


class AbilityCasts:
    def __init__(self, agent: Agent, data: AbilityCastsPayload):
        self.agent: Agent = agent
        self._grenade_casts: int = data['grenadeCasts']
        self._ability1_casts: int = data['ability1Casts']
        self._ability2_casts: int = data['ability2Casts']
        self._ultimate_casts: int = data['ultimateCasts']

    @property
    def e_casts(self) -> int:
        return self._ability2_casts

    @property
    def q_casts(self) -> int:
        return self._ability1_casts

    @property
    def c_casts(self) -> int:
        return self._grenade_casts

    @property
    def x_casts(self) -> int:
        return self._ultimate_casts

    def __repr__(self) -> str:
        attrs = [
            ('e_casts', self.e_casts),
            ('q_casts', self.q_casts),
            ('c_casts', self.c_casts),
            ('x_casts', self.x_casts),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def get_ability(self, slot: AbilityType) -> AgentAbility:
        for skill in self.agent.abilities:
            if skill.slot == slot:
                return skill

    @property
    def e(self) -> AgentAbility:
        return self.get_ability(AbilityType.ability_2)

    @property
    def q(self) -> AgentAbility:
        return self.get_ability(AbilityType.ability_1)

    @property
    def c(self) -> AgentAbility:
        return self.get_ability(AbilityType.grenade)

    @property
    def x(self) -> AgentAbility:
        return self.get_ability(AbilityType.ultimate)


class MatchPlayer(Player):
    def __init__(self, *, client: Client, data: PlayerMatchPayload, match: MatchDetails) -> None:
        super().__init__(client=client, data=data)
        self.match = match
        self._character_id: str = data['characterId']
        self._team_id: str = data['teamId']
        self.party: Party = Party(data, match)
        self.party_id: str = data['partyId']
        self._is_winner: bool = False
        self.play_time_seconds: float = data['stats']['playtimeMillis'] / 1000
        self.account_level: int = data.get('accountLevel', 1)

        self.player_card: PlayerCard = client.get_player_card(uuid=data['playerCard'])
        self.player_title: PlayerTitle = client.get_player_title(uuid=data['playerTitle'])
        self.level_border: Optional[LevelBorder] = client.get_level_border(uuid=data.get('preferredLevelBorder', None))

        self._competitive_rank: int = data['competitiveTier']
        self.platform: Platform = Platform(data['platformInfo'])
        self._round_damage: Optional[List[RoundDamagePayload]] = data.get('roundDamage') or []

        # stats
        self.score: int = data['stats']['score']
        self.kills: int = data['stats']['kills']
        self.deaths: int = data['stats']['deaths']
        self.assists: int = data['stats']['assists']
        self.rounds_played: int = data['stats']['roundsPlayed']
        self.first_kills: int = 0
        self.first_deaths: int = 0
        self.plants: int = 0
        self.defuses: int = 0
        self.damages: int = 0
        self.head_shots: int = 0
        self.body_shots: int = 0
        self.leg_shots: int = 0
        self.head_shot_percent: float = 0
        self.body_shot_percent: float = 0
        self.leg_shot_percent: float = 0
        self.clutches: int = 0  # TODO: implement
        self.afk_time: int = 0
        self.penalized_time: int = 0
        self.stayed_in_spawn: int = 0

        # stats plus
        self.multi_kills: int = 0  # kill more than 3 enemies in a round
        self.ace: int = 0  # kill all enemies in a round
        self.head_shot_percent: float = 0
        self.body_shot_percent: float = 0
        self.leg_shot_percent: float = 0
        # self.weapon_stats: Dict[str, Any] = {}

        # abilities
        self.ability_casts: Optional[AbilityCasts] = (
            AbilityCasts(self.agent, data['stats']['abilityCasts']) if data['stats'].get('abilityCasts') else None
        )

        # behavior
        behavior = data['behaviorFactors']
        self.afk_rounds: int = behavior.get('afkRounds')
        self.collisions: float = behavior.get('collisions', 0.0)
        self.damage_participation_out_going: int = behavior.get('damageParticipationOutgoing')
        self.friendly_fire_in_coming: int = behavior.get('friendlyFireIncoming', 0)
        self.friendly_fire_out_going: int = behavior.get('friendlyFireOutgoing', 0)
        self.mouse_movement: int = behavior.get('mouseMovement')
        self.stayed_in_spawn_rounds: int = behavior.get('stayedInSpawnRounds', 0)

        # other info
        self.session_playtime_minutes: int = data.get('sessionPlaytimeMinutes', 0)

        # TODO: Model this
        self.xp_modifications: List[xpModificationPayload] = data.get('xpModifications', [])
        self.new_player_exp_details: NewPlayerExperienceDetailsPayload = data['newPlayerExperienceDetails']

        self.last_update = match.started_at

    def __repr__(self) -> str:
        return f'<PlayerMatch display_name={self.display_name!r} agent={self.agent!r} team={self.team!r}>'

    def fill_player_stats(self) -> None:

        for round_result in self.match.round_results:

            # spikes
            if round_result.spike.is_planted():
                if round_result.spike.plater() == self:
                    self.plants += 1

            if round_result.spike.is_defused():
                if round_result.spike.defuser() == self:
                    self.defuses += 1

            death_on_round = []
            for stat in round_result.player_stats:
                for kill in stat.kills:
                    death_on_round.append(kill)

                if stat.player == self:
                    for dmg in stat.damage:
                        self.head_shots += dmg.head_shots
                        self.body_shots += dmg.body_shots
                        self.leg_shots += dmg.leg_shots
                        self.damages += dmg.damage

                    # kills
                    if len(stat.kills) > 3:
                        self.multi_kills += 1

                    if len(stat.kills) == 5:
                        self.ace += 1

                    # # score
                    # self.score += stat.score

                    # behavior
                    if stat.was_afk():
                        self.afk_time += 1

                    if stat.was_penalized():
                        self.penalized_time += 1

                    if stat.stayed_in_spawn():
                        self.stayed_in_spawn += 1

                    # self._ability_stats = stat.

            # find first blood and first death
            for player_death in sorted(death_on_round, key=lambda x: x.round_time):
                if player_death.killer == self:
                    self.first_kills += 1
                if player_death.victim == self:
                    self.first_deaths += 1
                break

        for team in self.match.teams:
            if team.is_won():
                if team == self.team:
                    self._is_winner = True

        with contextlib.suppress(ZeroDivisionError):
            hs_percent, bs_percent, ls_percent = utils.percent(self.head_shots, self.body_shots, self.leg_shots)
            self.head_shot_percent, self.body_shot_percent, self.leg_shot_percent = (
                hs_percent,
                bs_percent,
                ls_percent,
            )

    def get_opponent(self, player_opponent: MatchPlayer) -> Opponent:
        if player_opponent.team == self.team:
            raise ValueError('Player Opponent is your teammate')
        return Opponent(self.match, self, player_opponent)

    def is_winner(self) -> bool:
        return self._is_winner

    @property
    def team(self) -> Optional[Team]:
        return self.match.get_team(self._team_id)

    @property
    def agent(self) -> Agent:
        """player's agent"""
        return self._client.get_agent(uuid=self._character_id)

    @property
    def character(self) -> Agent:
        """alias for :meth:`agent`"""
        return self.agent

    @property
    def round_damage(self) -> List[RoundDamage]:
        """list of :class:`RoundDamage`"""
        return [RoundDamage(self.match, data) for data in self._round_damage]

    def get_party_members(self) -> List[Optional[MatchPlayer]]:
        return [player for player in self.match._players if player.party_id == self.party_id and player.puuid != self.puuid]

    @property
    def average_combat_score(self) -> float:
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

    @property
    def opponents(self) -> List[Opponent]:
        return [self.get_opponent(opponent) for opponent in self.match._players if opponent.team != self.team]

    @property
    def kda(self) -> str:
        """:class:`str`: kills/deaths/assists"""
        return f'{self.kills}/{self.deaths}/{self.assists}'

    @property
    def acs(self) -> float:
        """:class:`str`: average combat score"""
        return self.average_combat_score

    def get_competitive_rank(self) -> Optional[Tier]:
        """:class:`Tier`: player's competitive rank"""
        season = self.match.get_season()
        return self._client.get_tier(self._competitive_rank, season)

    async def fetch_competitive_rank(self) -> Optional[Tier]:
        """|coro|

        Fetch player's competitive rank

        Returns
        -------
        Optional[:class:`Tier`]
            player's competitive rank
        """
        if tier := self.get_competitive_rank() is not None:
            return tier
        season = self.match.get_season()
        mmr = await self._client.fetch_mmr(puuid=self.puuid)
        return mmr.get_last_rank_tier(season=season)


class Coach(Player):
    def __init__(self, match: MatchDetails, data: CoachPayload) -> None:
        super().__init__(client=match._client, data=data)
        self.match = match
        self.subject: str = data['subject']
        self.team_id: str = data['teamId']

    def __repr__(self) -> str:
        return f'<Coach display_name={self.display_name!r} team_id={self.team_id!r}>'

    @property
    def team(self) -> Team:
        return self.match.get_team(self.team_id)


class MatchDetails:
    def __init__(self, client: Client, data: MatchDetailsPayload) -> None:
        self._client = client
        self._match_info = match_info = data['matchInfo']
        self.id: str = match_info.get('matchId')
        self._map_url: str = match_info.get('mapId')
        self._game_pod_id: str = match_info.get('gamePodId')
        self._game_loop_zone: str = match_info.get('gameLoopZone')
        self._game_server_address: str = match_info.get('gameServerAddress')
        self._game_version: str = match_info.get('gameVersion')
        self._game_length: int = match_info.get('gameLengthMillis')
        self._game_start_millis: int = match_info.get('gameStartMillis')
        self._provisioning_FlowID: str = match_info.get('provisioningFlowID')
        self._is_completed: bool = match_info.get('isCompleted')
        self._custom_game_name: str = match_info.get('customGameName')
        self._force_post_processing: bool = match_info.get('forcePostProcessing')
        self._queue_id: QueueID = try_enum(QueueID, match_info.get('queueID'))
        self._game_mode: str = match_info.get('gameMode')
        self._is_ranked: bool = match_info.get('isRanked', False)
        self._is_match_sampled: bool = match_info.get('isMatchSampled')
        self._season_id: str = match_info.get('seasonId')
        self._completion_state: str = match_info.get('completionState')
        self._platform_type: str = match_info.get('platformType')
        self._should_match_disable_penalties: bool = match_info.get('shouldMatchDisablePenalties')
        self._is_won: bool = False
        self._is_surrendered: bool = False
        self._players: List[MatchPlayer] = [
            MatchPlayer(client=self._client, data=player, match=self) for player in data['players']
        ]
        self._coaches: List[Dict[str, Any]] = data['coaches']
        self._bots: List[Dict[str, Any]] = data['bots']
        # self._kills: List[MatchKillPayload] = data['kills']
        self._teams: List[MatchTeamPayload] = data['teams']
        self._round_results: List[RoundResult] = (
            [RoundResult(self, data) for data in data['roundResults']] if data.get('roundResults') else []
        )
        self.__fill_player_stats()
        if str(self._queue_id) == '' and self._provisioning_FlowID == 'CustomGame':
            self._queue_id = QueueID.custom

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

    def __fill_player_stats(self):
        for player in self._players:
            player.fill_player_stats()

    @property
    def user(self) -> Any:
        """:class:`Any`: The user who fetched this match."""
        return self._client.user

    def is_won(self) -> bool:
        """:class:`bool`: Whether the user won this match."""
        return self._is_won

    def is_ranked(self) -> bool:
        """:class:`bool`: Whether this match was ranked."""
        return self._is_ranked

    def is_completed(self) -> bool:
        """:class:`bool`: Whether this match was completed."""
        return self._is_completed

    def is_match_sampled(self) -> bool:
        """ " :class:`bool`: Whether this match was sampled."""
        return self._is_match_sampled

    def is_surrendered(self) -> bool:
        """:class:`bool`: Whether the user surrendered this match."""
        return self._is_surrendered

    def should_match_disable_penalties(self) -> bool:
        """:class:`bool`: Whether this match disabled penalties."""
        return self._should_match_disable_penalties

    @property
    def map(self) -> Map:
        """:class:`Map`: The map this match was played on."""
        to_uuid = MapID.from_url(self._map_url)
        return self._client.get_map(uuid=to_uuid)

    @property
    def game_mode(self) -> Optional[GameMode]:
        """:class:`GameMode`: The game mode this match was played in."""
        return self._client.get_game_mode(uuid=GameModeID.from_url(self._game_mode))

    @property
    def started_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The time this match started."""
        return datetime.datetime.fromtimestamp(self._game_start_millis / 1000)

    @property
    def game_length(self) -> int:
        """Returns the length of the game in seconds"""
        return self._game_length // 1000

    @property
    def queue(self) -> QueueID:
        return self._queue_id

    @property
    def bots(self) -> List[Any]:
        """:class:`List[Any]`: Returns a list of bots in the match"""
        return self._bots

    @property
    def teams(self) -> List[Team]:
        """:class:`List[Any]`: Returns a list of teams in the match"""
        return [Team(data=team, match=self) for team in self._teams]

    @property
    def coaches(self) -> List[Coach]:
        """:class:`List[Any]`: Returns a list of coaches in the match"""
        return [Coach(match=self, data=coach) for coach in self._coaches]

    @property
    def round_results(self) -> List[RoundResult]:
        """:class:`List[RoundResult]`: Returns a list of round results in the match"""
        return self._round_results

    @property
    def kills(self) -> Iterator[Kill]:
        """:class:`Iterator[Kill]`: Returns a list of kills in the match"""
        for round_result in self.round_results:
            for player in round_result.player_stats:
                yield from player.kills

    @property
    def me(self) -> Optional[MatchPlayer]:
        """Returns the :class:`MatchPlayer` object for the current user"""
        for player in self._players:
            if player.puuid == self._client.user.puuid:
                return player
        return None

    @property
    def team_blue(self) -> Optional[Team]:
        """:class:`Team`: The blue team in this match."""
        for team in self.teams:
            if team.id.lower() == 'blue':
                return team
        return None

    @property
    def team_red(self) -> Optional[Team]:
        """:class:`Team`: The red team in this match."""
        for team in self.teams:
            if team.id.lower() == 'red':
                return team
        return None

    def get_enemy_team(self) -> Optional[Team]:
        """:class:`Team`: The enemy team in this match."""
        for team in self.teams:
            if self.me.team != team:
                return team
        return None

    def get_me_team(self) -> Optional[Team]:
        """:class:`Team`: The team the current user is on."""
        return self.me.team

    def get_player(self, uuid: str) -> Optional[MatchPlayer]:
        """Returns the :class:`MatchPlayer` object for the given uuid"""
        for player in self._players:
            if player.puuid == uuid:
                return player
        return None

    def get_team(self, id_: str) -> Optional[Team]:
        """Returns the :class:`Team` object for the given uuid"""
        for team in self.teams:
            if team.id.lower() == id_.lower():
                return team
        return None

    def get_season(self) -> Season:
        return self._client.get_season(uuid=self._season_id)

    def get_players(self) -> List[MatchPlayer]:
        return self._players

    def get_enemy_players(self) -> List[MatchPlayer]:
        return [player for player in self._players if player.team != self.me.team]

    def get_me_team_players(self) -> List[MatchPlayer]:
        return [player for player in self._players if player.team == self.me.team]


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
