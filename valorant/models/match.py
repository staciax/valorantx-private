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

from ..enums import MapID, QueueID, try_enum
from .map import Map
from .player import MatchPlayer

if TYPE_CHECKING:
    from ..client import Client
    from ..types.match import (
        MatchDetails as MatchDetailsPayload,
        MatchHistory as MatchHistoryPayload,
        MatchHistoryList as MatchHistoryListPayload,
        MatchKill as MatchKillPayload,
        MatchRoundResult as MatchRoundResultPayload,
        Team as MatchTeamPayload,
    )

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
