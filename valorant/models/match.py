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
import datetime
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

from ..enums import MapID, QueueID, RoundResultCode, RoundResultType, try_enum
from .map import Map
from .player import MatchPlayer

if TYPE_CHECKING:
    from ..client import Client
    from ..types.match import (
        Location as MatchLocationPayload,
        MatchDetails as MatchDetailsPayload,
        MatchHistory as MatchHistoryPayload,
        MatchHistoryList as MatchHistoryListPayload,
        MatchKill as MatchKillPayload,
        MatchRoundResult as MatchRoundResultPayload,
        PlayerEconomy as MatchPlayerEconomyPayload,
        PlayerLocation as MatchPlayerLocationPayload,
        Team as MatchTeamPayload,
    )
    from .gear import Gear
    from .weapons import Weapon

__all__ = (
    'MatchHistory',
    'MatchDetails',
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


class PlayerEconomy:
    def __init__(self, match: MatchDetails, data: MatchPlayerEconomyPayload):
        self.match: MatchDetails = match
        self.subject: str = data.get('subject')
        self.player: Optional[MatchPlayer] = match.get_player(self.subject)
        self.loadout_value: int = data.get('loadoutValue', 0)
        self._weapon: Optional[str] = data.get('weapon') if data.get('weapon') == '' else None
        self._armor: Optional[str] = data.get('armor') if data.get('armor') == '' else None
        self.remaining: int = data.get('remaining', 0)
        self.spent: int = data.get('spent', 0)

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


class MatchPlayerLocation:
    def __init__(self, data: MatchPlayerLocationPayload) -> None:
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


class RoundResult:
    def __init__(self, match: MatchDetails, data: MatchRoundResultPayload) -> None:
        self.match: MatchDetails = match
        self.round_number: int = data.get('roundNum', 0)
        self.result: RoundResultType = try_enum(RoundResultType, data.get('roundResult'))
        self.winning_team: Team = ...
        # TODO: plant object
        # TODO: defuse object
        self.plant_player_locations: List[MatchPlayerLocation] = (
            [MatchPlayerLocation(x) for x in data['plantPlayerLocations']] if data.get('plantPlayerLocations') else []
        )
        self.plant_location: Optional[Location] = Location(data['plantLocation']) if data.get('plantLocation') else None
        self.plant_site: Optional[str] = data.get('plantSite', None)
        self.defuse_round_time: int = data.get('defuseRoundTime', 0)
        self.defuse_player_Locations: List[MatchPlayerLocation] = (
            [MatchPlayerLocation(x) for x in data['defusePlayerLocations']] if data.get('defusePlayerLocations') else []
        )
        self.defuse_location: Optional[Location] = Location(data['defuseLocation']) if data.get('defuseLocation') else None
        self.result_code: RoundResultCode = try_enum(RoundResultCode, data.get('roundResultCode', ''))
        self._ceremony: Optional[str] = data.get('roundCeremony', None)
        self.player_economies: List[PlayerEconomy] = (
            [PlayerEconomy(match, economy) for economy in data['playerEconomies']] if data.get('playerEconomies') else []
        )
        self.player_scores: List[Any] = data.get('playerScores', [])
        self.player_stats: List[Any] = data.get('playerStats', [])

    def __int__(self) -> int:
        return self.round_number

    def __bool__(self) -> bool:
        return self.match.me == self.winning_team


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
        self._my_team: Optional[str] = None
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

    # @property
    # def user(self) -> Any:
    #     return self._client.user

    def is_won(self) -> bool:
        return self._is_won

    def is_ranked(self) -> bool:
        return self._is_ranked

    @property
    def map(self) -> Map:
        to_uuid = MapID.from_url(self._map_url)
        return Map._from_uuid(client=self._client, uuid=to_uuid)

    def my_team(self) -> str:
        return self._my_team

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
    def teams(self) -> List[Any]:
        """:class:`List[Any]`: Returns a list of teams in the match"""
        return self._teams

    @property
    def coaches(self) -> List[Any]:
        """:class:`List[Any]`: Returns a list of coaches in the match"""
        return self._coaches

    @property
    def round_results(self) -> List[Dict[str, Any]]:
        """:class:`List[Mapping[str, Any]]`: Returns a list of rounds in the match"""
        return self._round_results

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
