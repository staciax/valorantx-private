from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from ..enums import ItemTypeID, try_enum
from .party import PlayerIdentity
from .sprays import Spray

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.sprays import Spray as SprayPayloadValorantAPI
    from valorantx.valorant_api_cache import CacheState

    from ..client import Client
    from ..types.coregame import (
        Loadout as LoadoutPayload,
        LoadoutChild as LoadoutChildPayload,
        Match as MatchPayload,
        MatchmakingData as MatchmakingDataPayload,
        MatchPlayer as MatchPlayerPayload,
        Player as PlayerPayload,
        SeasonalBadgeInfo as SeasonalBadgeInfoPayload,
        SpraySelection as SpraySelectionPayload,
    )
    from .agents import Agent
    from .competitive_tiers import Tier
    from .gamemodes import GameMode
    from .maps import Map
    from .seasons import Season
    from .weapons import Skin, SkinChroma, SkinLevel

_log = logging.getLogger(__name__)

__all__ = (
    'CoreGameMatch',
    'CoreGameMatchPlayer',
    'CoreGamePlayer',
    'MatchmakingData',
)


class CoreGamePlayer:
    def __init__(self, client: Client, data: PlayerPayload) -> None:
        self._client: Client = client
        self._update(data)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} subject={self.subject!r} match_id={self.match_id!r} version={self.version!r}>'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CoreGamePlayer)
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

    async def fetch_match(self) -> CoreGameMatch:
        return await self._client.fetch_coregame_match(self.match_id)


class MatchmakingData:
    def __init__(self, data: MatchmakingDataPayload) -> None:
        self.queue_id: str = data['QueueID']
        self._is_ranked: bool = data['IsRanked']

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} queue_id={self.queue_id!r} is_ranked={self.is_ranked()!r}>'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, MatchmakingData) and other.queue_id == self.queue_id and other.is_ranked() == self.is_ranked()
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def is_ranked(self) -> bool:
        return self._is_ranked


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


class CoreGameMatchPlayer:
    def __init__(self, client: Client, data: MatchPlayerPayload) -> None:
        self._client: Client = client
        self.subject: str = data['Subject']
        self.team_id: Union[str, Literal['Blue', 'Red']] = data['TeamID']
        self.character_id: str = data['CharacterID']
        self.player_identity: PlayerIdentity = PlayerIdentity(client, data['PlayerIdentity'])
        self._is_coach: bool = data['IsCoach']
        self._is_associated: bool = data['IsAssociated']

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} id={self.id!r} character={self.character!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CoreGameMatchPlayer) and other.id == self.id

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


class CoreGameMatch:
    def __init__(self, client: Client, data: MatchPayload) -> None:
        self._client: Client = client
        self._update(data)

    def __repr__(self) -> str:
        return f'<CoreGameMatch id={self.id!r} version={self.version!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CoreGameMatch) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    def _update(self, data: MatchPayload) -> None:
        self.id: str = data['MatchID']
        self.version: int = data['Version']
        self.state: Literal['IN_PROGRESS'] = data['State']
        self.map_id: str = data['MapID']
        self.mode_id: str = data['ModeID']
        self.provisioning_flow: Literal['Matchmaking', 'CustomGame'] = data['ProvisioningFlow']
        self.game_pod_id: str = data['GamePodID']
        self.all_muc_name: str = data['AllMUCName']
        self.team_muc_name: str = data['TeamMUCName']
        self.team_voice_id: str = data['TeamVoiceID']
        self._is_reconnectable: bool = data['IsReconnectable']
        self.post_game_details: Optional[Any] = data['PostGameDetails']
        self.players: List[CoreGameMatchPlayer] = [CoreGameMatchPlayer(self._client, p) for p in data['Players']]
        self.matchmaking_data: Optional[MatchmakingData] = None
        if data['MatchmakingData'] is not None:
            self.matchmaking_data = MatchmakingData(data['MatchmakingData'])

    @property
    def map(self) -> Optional[Map]:
        map_ = self._client.valorant_api.get_map(self.map_id)
        if map_ is None:
            _log.warning(f'Unknown map ID {self.map_id!r}')
            return None
        return map_

    @property
    def mode(self) -> Optional[GameMode]:
        mode = self._client.valorant_api.get_game_mode(self.mode_id)
        if mode is None:
            _log.warning(f'Unknown mode ID {self.mode_id!r}')
            return None
        return mode

    def is_reconnectable(self) -> bool:
        return self._is_reconnectable

    def is_ranked(self) -> bool:
        if self.matchmaking_data is None:
            return False
        return self.matchmaking_data.is_ranked()

    async def refresh(self) -> None:
        data = await self._client.http.get_coregame_match(self.id)
        self._update(data)

    async def fetch_loadouts(self) -> List[CoreGameLoadouts]:
        data = await self._client.http.get_coregame_match_loadouts(self.id)
        loadouts = []
        for loadout in data['Loadouts']:
            loadouts.append(CoreGameLoadouts(self._client, loadout))
        return loadouts


class SprayCoreGameLoadout(Spray):
    def __init__(
        self,
        *,
        state: CacheState,
        data: SprayPayloadValorantAPI,
        favorite: bool = False,
        data_coregame: SpraySelectionPayload,
    ) -> None:
        super().__init__(state=state, data=data, favorite=favorite)
        self.socket_id: str = data_coregame['SocketID']
        self.level_id: str = data_coregame['LevelID']

    @classmethod
    def from_coregame_loadout(cls, client: Client, data: SpraySelectionPayload) -> Optional[Self]:
        spray = client.valorant_api.get_spray(data['SprayID'])
        if spray is None:
            _log.warning(f'Unknown spray ID {data["SprayID"]!r}')
            return None
        self = cls._copy(spray)  # type: ignore
        self.socket_id = data['SocketID']
        self.level_id = data['LevelID']
        return self


class Loadout:
    def __init__(self, client: Client, data: LoadoutPayload) -> None:
        self._client: Client = client
        self.sprays: List[SprayCoreGameLoadout] = []
        self.items: List[Union[Skin, SkinLevel, SkinChroma, Any]] = []
        for spray in data['Sprays']['SpraySelections']:
            spray_id = spray['SprayID']
            spray = SprayCoreGameLoadout.from_coregame_loadout(client, spray)
            if spray is None:
                _log.warning(f'Unknown spray ID {spray_id!r}')
                continue
            self.sprays.append(spray)
        for item_id, item_data in data['Items'].items():
            for socket_id, socket_data in item_data['Sockets'].items():
                item = socket_data['Item']
                item_id = item['ID']
                item_type = try_enum(ItemTypeID, socket_id)
                if item_type == ItemTypeID.weapon_skin:
                    skin = client.valorant_api.get_skin(item_id)
                    if skin is None:
                        _log.warning(f'Unknown skin ID {item_id!r}')
                        continue
                    self.items.append(skin)
                if item_type == ItemTypeID.skin_level:
                    skin_level = client.valorant_api.get_skin_level(item_id)
                    if skin_level is None:
                        _log.warning(f'Unknown skin level ID {item_id!r}')
                        continue
                    self.items.append(skin_level)
                if item_type == ItemTypeID.skin_chroma:
                    skin_chroma = client.valorant_api.get_skin_chroma(item_id)
                    if skin_chroma is None:
                        _log.warning(f'Unknown skin chroma ID {item_id!r}')
                        continue
                    self.items.append(skin_chroma)


class CoreGameLoadouts:
    def __init__(self, client: Client, data: LoadoutChildPayload) -> None:
        self._client: Client = client
        self.character_id: str = data['CharacterID']
        self.loadout: Loadout = Loadout(client, data['Loadout'])

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} character={self.character!r}>'

    @property
    def character(self) -> Optional[Agent]:
        agent = self._client.valorant_api.get_agent(self.character_id)
        if agent is None:
            _log.warning(f'Unknown agent ID {self.character_id!r}')
            return None
        return agent
