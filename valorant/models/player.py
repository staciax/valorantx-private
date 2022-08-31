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

import contextlib
import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from .. import utils
from ..enums import LevelBorderID
from .agent import Agent
from .level_border import LevelBorder
from .player_card import PlayerCard
from .player_title import PlayerTitle

if TYPE_CHECKING:
    from ..client import Client
    from ..types.match import (
        RoundDamage as RoundDamagePayload,
        newPlayerExperienceDetails as newPlayerExperienceDetailsPayload,
        xpModification as xpModificationPayload,
    )
    from ..types.player import (
        PartialPlayer as PartialPlayerPayload,
        Player as PlayerPayload,
        PlayerMatch as PlayerMatchPayload,
    )
    from .match import MatchDetails

# fmt: off
__all__ = (
    'BasePlayer',
    'MatchPlayer',
    'ClientPlayer',

)
# fmt: on


class _PlayerTag:
    __slots__ = ()
    puuid: str


class BasePlayer(_PlayerTag):

    __slots__ = (
        'name',
        '_puuid',
        'tagline',
        'region',
        '_client',
        'account_level',
        '_player_card_id',
        '_player_title_id',
        '_level_border_id',
    )

    if TYPE_CHECKING:
        name: str
        # puuid: str
        _puuid: Optional[str]
        tagline: str
        region: str
        _client: Client
        _player_card_id: Optional[str]
        _player_title_id: Optional[str]
        _level_border_id: Optional[str]

    def __init__(
        self,
        *,
        client: Client,
        data: Union[PlayerPayload, PartialPlayerPayload],
    ) -> None:
        self._client = client
        self._puuid: str = data.get('puuid', None) or data.get('Subject', None) or data.get('subject', None)
        self._update(data)

    def __str__(self) -> str:
        return f'{self.name}#{self.tagline}'

    def __repr__(self) -> str:
        return f"<Player puuid={self.puuid!r} name={self.name!r} tagline={self.tagline!r} region={self.region!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _PlayerTag) and other.puuid == self.puuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.puuid)

    def _update(self, data: Union[PlayerPayload, PartialPlayerPayload]) -> None:
        self.name: Optional[str] = data.get('username', None) or data.get('gameName', None)
        self.tagline: Optional[str] = data.get('tagline', None) or data.get('tagLine', None)
        self.region: Optional[str] = data.get('region', None)
        self.account_level: int = 0
        self._player_card_id: Optional[str] = None
        self._player_title_id: Optional[str] = None
        self._level_border_id: Optional[str] = None

    @property
    def puuid(self) -> str:
        # if not self._puuid:
        #     self._puuid = self._client.fetch_player_by_name(self.name, self.tagline)
        return self._puuid

    @property
    def display_name(self) -> str:
        if self.name is None and self.tagline is None:
            return 'Unknown'
        return f"{self.name}#{self.tagline}"

    @property
    def player_card(self) -> Optional[PlayerCard]:
        if hasattr(self, '_player_card'):
            return PlayerCard._from_uuid(self._client, self._player_card_id) if self._player_card_id else None
        return None

    @property
    def player_title(self) -> Optional[PlayerTitle]:
        if hasattr(self, '_player_title_id'):
            return PlayerTitle._from_uuid(self._client, self._player_title_id) if self._player_title_id else None
        return None

    @property
    def level_border(self) -> LevelBorder:
        if hasattr(self, '_level_border_id'):
            return LevelBorder._from_uuid(self._client, self._level_border_id)
        return LevelBorder._from_uuid(self._client, LevelBorderID._1)

    @property
    def mmr(self) -> int:
        return self.mmr

    @property
    def last_update(self) -> datetime:
        return ...


class ClientPlayer(BasePlayer):
    def __init__(self, *, client: Client, data: PlayerPayload) -> None:
        super().__init__(client=client, data=data)
        self.locale: str = data.get('locale', None)

    def __repr__(self) -> str:
        return f'<ClientPlayer puuid={self.puuid!r} name={self.name!r} tagline={self.tagline!r} region={self.region!r}'


class MatchPlayer(BasePlayer):

    # https://github.com/staciax/reinabot/blob/master/cogs/valorant/embeds.py

    def __init__(self, *, client: Client, data: PlayerMatchPayload, match_details: MatchDetails) -> None:
        super().__init__(client=client, data=data)
        self.match_details = match_details
        self._character_id: str = data['characterId']
        self.team: str = data['teamId']
        self.party_id: str = data['partyId']
        self._is_winner: bool = False
        self.play_time_seconds: float = data['stats']['playtimeMillis'] / 1000
        self.account_level: int = data['accountLevel']
        self._player_card_id: str = data['playerCard']
        self._player_title_id: str = data['playerCard']
        self._level_border_id: str = data.get('preferredLevelBorder', str(LevelBorderID._1))
        self._competitive_rank: int = data['competitiveTier']

        # platform info   # TODO: Objectify this
        self.platform_type: str = data['platformInfo']['platformType']
        self.platform_os: str = data['platformInfo']['platformOS']
        self.platform_os_version: str = data['platformInfo']['platformOSVersion']
        self.platform_chipset: str = data['platformInfo']['platformChipset']

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
        self.session_playtime_minutes: int = data['sessionPlaytimeMinutes']
        self.xpModifications: List[xpModificationPayload] = data.get('xpModifications', [])

        # new player
        self.new_player_exp_details: newPlayerExperienceDetailsPayload = data['newPlayerExperienceDetails']

        self.__fill_match_data()

    def __repr__(self) -> str:
        return f'<PlayerMatch uuid={self.puuid!r} name={self.name!r} tagline={self.tagline!r} region={self.region!r}>'

    def __fill_match_data(self) -> None:

        for round_result in self.match_details.round_results:
            death_on_round = []
            for stat in round_result['playerStats']:
                for kill in stat['kills']:
                    death_on_round.append(dict(killer=kill['killer'], victim=kill['victim'], round_time=kill['roundTime']))

                if stat['subject'] == self.puuid:
                    for dmg in stat['damage']:
                        self.head_shots += dmg['headshots']
                        self.body_shots += dmg['bodyshots']
                        self.leg_shots += dmg['legshots']

            if death_on_round:
                first_blood = sorted(death_on_round, key=lambda x: x['round_time'])[0]
                if first_blood['killer'] == self.puuid:
                    self.first_blood += 1

                if first_blood['victim'] == self.puuid:
                    self.first_death += 1

        with contextlib.suppress(ZeroDivisionError):
            hs_percent, bs_percent, ls_percent = utils.percent(self.head_shots, self.body_shots, self.leg_shots)
            self.headshot_percent, self.bodyshot_percent, self.legshot_percent = hs_percent, bs_percent, ls_percent

    def is_winner(self) -> bool:
        return self._is_winner

    def agent(self) -> Agent:
        """player's agent"""
        return Agent._from_uuid(client=self._client, uuid=self._character_id)

    def character(self) -> Agent:
        """player's character"""
        return self.agent()

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
