from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from .party import PlayerIdentity

if TYPE_CHECKING:
    from ..client import Client
    from ..types.pregame import (
        Match as MatchPayload,
        MatchPlayer as MatchPlayerPayload,
        Player as PlayerPayload,
        SeasonalBadgeInfo as SeasonalBadgeInfoPayload,
        Team as TeamPayload,
    )
    from .agents import Agent
    from .competitive_tiers import Tier
    from .gamemodes import GameMode
    from .maps import Map
    from .seasons import Season

_log = logging.getLogger(__name__)


__all__ = (
    'PreGameMatch',
    'PreGameMatchPlayer',
    'PreGamePlayer',
)


class PreGamePlayer:
    def __init__(self, client: Client, data: PlayerPayload) -> None:
        self._client: Client = client
        self._update(data)

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__} subject={self.subject!r} match_id={self.match_id!r} version={self.version!r}>'
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PreGamePlayer)
            and other.subject == self.subject
            and other.match_id == self.match_id
            and other.version == self.version
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.subject, self.match_id, self.version))

    def _update(self, data: PlayerPayload) -> None:
        self.subject = data['Subject']
        self.match_id = data['MatchID']
        self.version = data['Version']

    async def refresh(self) -> None:
        data = await self._client.http.get_pregame_player()
        self._update(data)

    async def fetch_match(self) -> PreGameMatch:
        return await self._client.fetch_pregame_match(self.match_id)

    async def select_character(self, character_id: str, /) -> PreGameMatch:
        data = await self._client.http.post_pregame_select_character(self.match_id, character_id)
        return PreGameMatch(self._client, data)

    async def lock_character(self, character_id: str, /) -> PreGameMatch:
        data = await self._client.http.post_pregame_lock_character(self.match_id, character_id)
        return PreGameMatch(self._client, data)

    async def quit(self) -> None:
        await self._client.http.post_pregame_quit_match(self.match_id)


class SeasonalBadgeInfo:
    def __init__(self, client: Client, data: SeasonalBadgeInfoPayload) -> None:
        self._client: Client = client
        self.season_id: str = data['SeasonID']
        self.number_of_wins: int = data['NumberOfWins']
        self.raw_wins_by_tier: Optional[Any] = data['WinsByTier']
        self.wins_by_tier: Dict[Tier, int] = {}
        self.rank: int = data['Rank']
        self.leaderboard_rank: int = data['LeaderboardRank']

    @property
    def season(self) -> Optional[Season]:
        if self.season_id == '':
            return None
        season = self._client.valorant_api.get_season(self.season_id)
        if season is None:
            _log.warning('Season %r not found', self.season_id)
        return season

    def __repr__(self) -> str:
        return f'<SeasonalBadgeInfo rank={self.rank!r} leaderboard_rank={self.leaderboard_rank!r}>'


class PreGameMatchPlayer:
    def __init__(self, client: Client, data: MatchPlayerPayload) -> None:
        self._client: Client = client
        self.subject: str = data['Subject']
        self.character_id: str = data['CharacterID']
        self.character_selection_state: Literal['', 'selected' 'locked'] = data['CharacterSelectionState']
        self.pregame_player_state: Literal['joined'] = data['PregamePlayerState']
        self.player_identity: PlayerIdentity = PlayerIdentity(client, data['PlayerIdentity'])
        self.seasonal_badge_info: SeasonalBadgeInfo = SeasonalBadgeInfo(client, data['SeasonalBadgeInfo'])
        self._is_captain: bool = data['IsCaptain']

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} character={self.character!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PreGameMatchPlayer) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self) -> str:
        return self.subject

    @property
    def character(self) -> Optional[Agent]:
        agent = self._client.valorant_api.get_agent(self.character_id)
        if agent is None:
            _log.warning(f'Unknown agent ID {self.character_id!r}')
            return None
        return agent

    def is_captain(self) -> bool:
        return self._is_captain


class Team:
    def __init__(self, client: Client, data: TeamPayload) -> None:
        self.team_id: str = data['TeamID']
        self.players: List[PreGameMatchPlayer] = [PreGameMatchPlayer(client, player) for player in data['Players']]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Team) and other.team_id == self.team_id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class PreGameMatch:
    def __init__(self, client: Client, data: MatchPayload) -> None:
        self._client: Client = client
        self._update(data)

    def __repr__(self) -> str:
        return f'<PreGameMatch id={self.id!r} version={self.version!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PreGameMatch) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    def _update(self, data: MatchPayload) -> None:
        self.id: str = data['ID']
        self.version: int = data['Version']
        self.teams: List[Team] = [Team(self._client, team) for team in data['Teams']]
        self.EnemyTeam: Optional[Team] = None
        if data['EnemyTeam'] is not None:
            self.EnemyTeam = Team(self._client, data['EnemyTeam'])
        self.observer_subjects: List[Any] = data['ObserverSubjects']
        self.match_coaches: List[Any] = data['MatchCoaches']
        self.enemy_team_size: int = data['EnemyTeamSize']
        self.enemy_team_lock_count: int = data['EnemyTeamLockCount']
        self.pregame_state: str = data['PregameState']
        self.last_updated: str = data['LastUpdated']
        self.map_id: str = data['MapID']
        self.map_select_pool: List[Any] = data['MapSelectPool']
        self.banned_map_ids: List[Any] = data['BannedMapIDs']
        self.casted_votes: Any = data['CastedVotes']
        self.map_select_steps: List[Any] = data['MapSelectSteps']
        self.map_select_step: int = data['MapSelectStep']
        self.team1: str = data['Team1']
        self.game_pod_id: str = data['GamePodID']
        self.mode_id: str = data['Mode']
        self.voice_session_id: str = data['VoiceSessionID']
        self.muc_name: str = data['MUCName']
        self.queue_id: str = data['QueueID']
        self.provisioning_flow_id: str = data['ProvisioningFlowID']
        self._is_ranked: bool = data['IsRanked']
        self.phase_time_remaining_ns: int = data['PhaseTimeRemainingNS']
        self.step_time_remaining_ns: int = data['StepTimeRemainingNS']
        self.alt_modes_flag_ada: bool = data['altModesFlagADA']
        self.tournament_metadata: Any = data['TournamentMetadata']
        self.roster_metadata: Any = data['RosterMetadata']

    @property
    def map(self) -> Optional[Map]:
        map_ = self._client.valorant_api.get_map_by_url(self.map_id)
        if map_ is None:
            _log.warning(f'Unknown map ID {self.map_id!r}')
            return None
        return map_

    @property
    def mode(self) -> Optional[GameMode]:
        gamemode = self._client.valorant_api.get_game_mode_by_url(self.mode_id)
        if gamemode is None:
            _log.warning(f'Unknown gamemode ID {self.mode!r}')
            return None
        return gamemode

    # @property
    # def last_updated(self) -> datetime.datetime:
    #     return datetime.datetime.fromisoformat(self._last_updated)

    def is_ranked(self) -> bool:
        return self._is_ranked

    async def refresh(self) -> None:
        data = await self._client.http.get_pregame_match(self.id)
        self._update(data)

    async def select_character(self, character_id: str, /) -> None:
        data = await self._client.http.post_pregame_select_character(self.id, character_id)
        self._update(data)

    async def lock_character(self, character_id: str, /) -> None:
        data = await self._client.http.post_pregame_lock_character(self.id, character_id)
        self._update(data)

    async def quit(self) -> None:
        await self._client.http.post_pregame_quit_match(self.id)
