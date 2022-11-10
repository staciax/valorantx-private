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

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Union

from .player import Player

if TYPE_CHECKING:
    from ..client import Client
    from ..enums import MapID
    from ..types.pre_game import PlayerPreGame as PlayerPreGamePayload, PreGameMatch as PreGameMatchPayload
    from .agent import Agent
    from .map import Map


class PlayerPreGame(Player):
    def __init__(self, *, client: Client, data: PlayerPreGamePayload) -> None:
        super().__init__(client=client, data=data)
        self._character_id: str = ''
        self._character_selection_state: str = ''
        self._competitive_tier: int = 0
        self._is_captain: bool = False
        self._incognito: bool = False
        self._hide_account_level: bool = False
        self._update(data)

    def _update(self, data: PlayerPreGamePayload) -> None:
        self._character_id = data['CharacterID']
        self._character_selection_state = data['CharacterSelectionState']
        self._competitive_tier = data['CompetitiveTier']
        self._is_captain = data['IsCaptain']

        identity = data['PlayerIdentity']

        player_card = self._client.get_player_card(uuid=identity.get('PlayerCardID'))
        if player_card is not None:
            self._player_card = player_card

        player_title = self._client.get_player_title(uuid=identity.get('PlayerTitleID'))
        if player_title is not None:
            self._player_title = player_title

        level_border = self._client.get_level_border(startingLevel=identity.get('PreferredLevelBorderID', 0))
        if level_border is not None:
            self._level_border = level_border

        self.account_level = identity.get('AccountLevel', self.account_level)
        self._incognito = identity.get('Incognito', self._incognito)
        self._hide_account_level = identity.get('HideAccountLevel', self._hide_account_level)

    def is_capitan(self) -> bool:
        return self._is_captain

    def incognito(self) -> bool:
        return self._incognito

    def hide_account_level(self) -> bool:
        return self._hide_account_level

    def is_selected(self) -> bool:
        return self._character_selection_state == 'selected'


class PreGameMatch:
    def __init__(self, client: Client, data: PreGameMatchPayload) -> None:
        self._client = client
        self.id: str = data['ID']
        self.version: int = data['Version']
        self._team: List[Any] = []
        self._ally_team: List[Any] = []
        self._enemy_team: List[Any] = []
        self._observer_subjects: List[Any] = []
        self._match_coach: List[Any] = []
        self._pre_game_state: str = data['PregameState']
        self.enemy_team_size: int = 0
        self.enemy_team_lock_count: int = 0
        self.pregame_state: str = data['PregameState']
        self._last_update: str = data['LastUpdated']
        self._map_id: str = data['MapID']
        self.map_select_pool: List[Any] = data['MapSelectPool']
        self.banned_map_ids: List[Any] = data['BannedMapIDs']
        self._casted_votes: Dict[str, Any] = data['CastedVotes']
        self.map_select_steps: int = data['MapSelectSteps']
        self.team1: str = data['Team1']
        self.game_pod_id: str = data['GamePodID']
        self.mode: str = data['Mode']
        self.voice_session_id: str = data['VoiceSessionID']
        self.muc_name: str = data['MUCName']
        self.queue_id: str = data['QueueID']
        self.provisioning_flow_id: str = data['ProvisioningFlowID']
        self._is_ranked: bool = False
        self._phase_time_remaining_ns: int = data['PhaseTimeRemainingNS']
        self._step_time_remaining_ns: int = data['StepTimeRemainingNS']
        self._alt_modes_flagADA: bool = data['altModesFlagADA']
        self._tournament_metadata: Optional[Any] = data['TournamentMetadata']
        self._roster_metadata: Optional[Any] = data['RosterMetadata']
        self._update(data)

    def _update(self, data: PreGameMatchPayload) -> None:
        self.enemy_team_size: int = data['EnemyTeamSize']
        self.enemy_team_lock_count: int = data['EnemyTeamLockCount']

    def is_ranked(self) -> bool:
        return self._is_ranked

    def map(self) -> Map:
        return self._client.get_map(uuid=str(MapID.from_url(self._map_id)))

    async def select_agent(self, agent: Agent, *, lock: bool = True) -> None:
        if lock:
            await self._client.http.pregame_lock_character(agent_id=agent.uuid, match_id=self.id)
        else:
            await self._client.http.pregame_select_character(agent_id=agent.uuid, match_id=self.id)

    async def lock_agent(self, agent: Agent) -> None:
        await self._client.http.pregame_lock_character(agent_id=agent.uuid, match_id=self.id)

    async def quit_match(self) -> None:
        await self._client.http.pregame_quit_match(match_id=self.id)

    async def fetch_match_loadouts(self) -> None:
        """Fetch match loadouts."""
        await self._client.http.pregame_fetch_match_loadouts(match_id=self.id)

    # status 500
    # async def fetch_chat_token(self) -> None:
    #     await self._client.http.pregame_fetch_chat_token(match_id=self.id)
    #
    # async def fetch_voice_token(self) -> None:
    #     await self._client.http.pregame_fetch_voice_token(match_id=self.id)
