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

from .. import utils
from ..asset import Asset
from ..enums import Locale, MapType
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from ..types.competitive import (
        MatchmakingRating as MatchmakingRatingPayload,
        QueueSkill as QueueSkillPayload,
        QueueSkills as QueueSkillsPayload,
        SeasonalInfo as SeasonalInfoPayload,
    )
    from .map import Map
    from .match import MatchDetails
    from .season import Season

__all__ = ('CompetitiveTier', 'MMR', 'Tier')


class Tier:
    def __init__(self, client: Client, data: Any) -> None:
        self._client: Client = client
        self.tier: int = data['tier']
        self._name: Dict[str, str] = data['tierName']
        self._division: Optional[str] = data['division']
        self._division_name: Dict[str, str] = data['divisionName']
        self.color: str = data['color']
        self.background_color: str = data['backgroundColor']
        self._small_icon: Optional[str] = data['smallIcon']
        self._large_icon: Optional[str] = data['largeIcon']
        self._rank_triangle_down_icon: Optional[str] = data['rankTriangleDownIcon']
        self._rank_triangle_up_icon: Optional[str] = data['rankTriangleUpIcon']
        self._name_locale: Localization = Localization(self._name, locale=self._client.locale)
        self._division_name_localized: Localization = Localization(self._division_name, locale=self._client.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Tier tier={self.tier!r} display_name={self.display_name!r} division={self.division!r}>'

    def __hash__(self) -> int:
        return hash(self.tier)

    def __eq__(self, other) -> bool:
        return isinstance(other, Tier) and self.tier == other.tier

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        return isinstance(other, Tier) and self.tier < other.tier

    def __le__(self, other: object) -> bool:
        return isinstance(other, Tier) and self.tier <= other.tier

    def __gt__(self, other: object) -> bool:
        return isinstance(other, Tier) and self.tier > other.tier

    def __ge__(self, other: object) -> bool:
        return isinstance(other, Tier) and self.tier >= other.tier

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._name_locale.from_locale(locale)

    def division_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._division_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the tier's name."""
        return self._name_locale

    @property
    def division(self) -> Optional[str]:
        """:class: `str` Returns the tier's division."""
        return utils.removeprefix(self._division, 'ECompetitiveDivision::') if self._division else None

    @property
    def division_name(self) -> Localization:
        """:class: `str` Returns the tier's division."""
        return self._division_name_localized

    @property
    def small_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the tier's small icon."""
        return Asset(self._client, self._small_icon) if self._small_icon else None

    @property
    def large_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the tier's large icon."""
        return Asset(self._client, self._large_icon) if self._large_icon else None

    @property
    def rank_triangle_down_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the tier's rank triangle down icon."""
        return Asset(self._client, self._rank_triangle_down_icon) if self._rank_triangle_down_icon else None

    @property
    def rank_triangle_up_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the tier's rank triangle up icon."""
        return Asset(self._client, self._rank_triangle_up_icon) if self._rank_triangle_up_icon else None


class CompetitiveTier(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self.asset_object_name: str = data['assetObjectName']
        self._tiers: List[Mapping[str, Any]] = data['tiers']
        self.asset_path: str = data['assetPath']

    def __str__(self) -> str:
        return self.asset_object_name

    def __repr__(self) -> str:
        return f'<CompetitiveTier asset_object_name={self.asset_object_name!r}>'

    def get_tiers(self) -> List[Tier]:
        """:class: `list` Returns the competitive tier's tiers."""
        return [Tier(client=self._client, data=tier) for tier in self._tiers]

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the competitive tier with the given UUID."""
        data = client._assets.get_competitive_tier(uuid)
        return cls(client=client, data=data) if data else None


class LatestCompetitiveUpdate:
    def __init__(self, client: Client, data: Any) -> None:
        self._client: Client = client
        self.match_id: str = data['MatchID']
        self._map_id: str = data['MapID']
        self._season_id: str = data['SeasonID']
        self.match_start_time: int = data['MatchStartTime']
        self.tier_after_update: int = data['TierAfterUpdate']
        self.tier_before_update: int = data['TierBeforeUpdate']
        self.ranked_rating_after_update: int = data['RankedRatingAfterUpdate']
        self.ranked_rating_before_update: int = data['RankedRatingBeforeUpdate']
        self.ranked_rating_earned: int = data['RankedRatingEarned']
        self.ranked_rating_performance_bonus: int = data['RankedRatingPerformanceBonus']
        self.afk_penalty: int = data['AFKPenalty']

    def __repr__(self) -> str:
        return f'<LatestCompetitiveUpdate season={self.season!r} map={self.map!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LatestCompetitiveUpdate) and self.match_id == other.match_id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def map(self) -> Optional[Map]:
        """:class: `Map` Returns the map."""
        to_uuid = MapType.from_url(self._map_id)
        return self._client.get_map(uuid=to_uuid)

    def season(self) -> Optional[Season]:
        """:class: `Season` Returns the season."""
        return self._client.get_season(uuid=self._season_id)

    async def fetch_match_details(self) -> Optional[MatchDetails]:
        """coro :class: `MatchDetails` Returns the match details."""
        return await self._client.fetch_match_details(self.match_id)


class SeasonalInfo:
    def __init__(self, client: Client, data: SeasonalInfoPayload) -> None:
        self._client: Client = client
        self.season_id: str = data['SeasonID']
        self.number_of_wins: int = data['NumberOfWins']
        self.number_of_games: int = data['NumberOfGames']
        self.rank: int = data['Rank']
        self.capstone_wins: int = data['CapstoneWins']
        self.leaderboard_rank: int = data['LeaderboardRank']
        self.competitive_tier_number: int = data['CompetitiveTier']
        self.ranked_rating: int = data['RankedRating']
        self.wins_by_tier: Dict[str, int] = data['WinsByTier']
        self.games_needed_for_rating: int = data['GamesNeededForRating']
        self.total_wins_needed_for_rank: int = data['TotalWinsNeededForRank']

    def __repr__(self) -> str:
        return f'<SeasonalInfo season={self.season!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SeasonalInfo) and self.season_id == other.season_id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def season(self) -> Optional[Season]:
        """:class: `Season` Returns the season."""
        return self._client.get_season(uuid=self.season_id)

    @property
    def tier(self) -> Optional[Tier]:
        """:class: `Tier` Returns the tier."""
        ss_com = self._client.get_season_competitive(seasonUuid=self.season_id)
        if ss_com is None:
            return None

        com_tiers = ss_com.get_competitive_tiers()
        if com_tiers is None:
            return None

        for tier in com_tiers.get_tiers():
            if tier.tier == self.competitive_tier_number:
                return tier

        return None


class QueueSkill:
    def __init__(self, client: Client, data: QueueSkillPayload) -> None:
        self._client: Client = client
        self.total_games_needed_for_rating: int = data['TotalGamesNeededForRating']
        self.total_games_needed_for_leaderboard: int = data['TotalGamesNeededForLeaderboard']
        self.current_season_games_needed_for_rating: int = data['CurrentSeasonGamesNeededForRating']
        self._seasonal_info_list: Dict[str, Any] = data['SeasonalInfoBySeasonID']

    def __repr__(self) -> str:
        attrs = [
            ('total_games_needed_for_rating', self.total_games_needed_for_rating),
            ('total_games_needed_for_leaderboard', self.total_games_needed_for_leaderboard),
            ('current_season_games_needed_for_rating', self.current_season_games_needed_for_rating),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def get_seasonal_info(self) -> Optional[List[SeasonalInfo]]:
        """:class: `list` Returns the seasonal info."""
        if self._seasonal_info_list is not None:
            return [
                SeasonalInfo(client=self._client, data=seasonal_info) for seasonal_info in self._seasonal_info_list.values()
            ]


class QueueSkills:
    def __init__(self, client: Client, data: QueueSkillsPayload) -> None:
        self._client: Client = client
        self.competitive: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['competitive']) if data.get('competitive') else None
        )
        self.custom: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['custom']) if data.get('custom') else None
        )
        self.deathmatch: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['deathmatch']) if data.get('deathmatch') else None
        )
        self.ggteam: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['ggteam']) if data.get('ggteam') else None
        )
        self.newmap: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['newmap']) if data.get('newmap') else None
        )
        self.onefa: Optional[QueueSkill] = QueueSkill(client=self._client, data=data['onefa']) if data.get('onefa') else None
        self.seeding: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['seeding']) if data.get('seeding') else None
        )
        self.snowball: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['snowball']) if data.get('snowball') else None
        )
        self.spikerush: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['spikerush']) if data.get('spikerush') else None
        )
        self.unrated: Optional[QueueSkill] = (
            QueueSkill(client=self._client, data=data['unrated']) if data.get('unrated') else None
        )

    def __repr__(self) -> str:
        attrs = [
            ('competitive', self.competitive),
            ('custom', self.custom),
            ('deathmatch', self.deathmatch),
            ('ggteam', self.ggteam),
            ('newmap', self.newmap),
            ('onefa', self.onefa),
            ('seeding', self.seeding),
            ('snowball', self.snowball),
            ('spikerush', self.spikerush),
            ('unrated', self.unrated),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'


class MMR(BaseModel):
    def __init__(self, client: Client, data: MatchmakingRatingPayload, **kwargs) -> None:
        super().__init__(client, data, **kwargs)
        self._uuid: str = data['Subject']
        self.version: int = data['Version']
        self.queue_skills: QueueSkills = QueueSkills(client, data['QueueSkills'])
        self._new_player_experience_finished: bool = data.get('NewPlayerExperienceFinished', False)
        self._is_leaderboard_anonymized: bool = data.get('IsLeaderboardAnonymized', False)
        self._is_act_rank_badge_hidden: bool = data.get('IsActRankBadgeHidden', False)
        self._latest_competitive_update: Optional[LatestCompetitiveUpdate] = LatestCompetitiveUpdate(
            client=self._client, data=data['LatestCompetitiveUpdate']
        )

    def __repr__(self) -> str:
        return f'<MMR version={self.version!r} latest_competitive_update={self.get_latest_competitive_update()!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MMR) and self.uuid == other.uuid and self.version == other.version

    def __hash__(self) -> int:
        return hash(self.uuid)

    def new_player_experience_finished(self) -> bool:
        """:class: `bool` Returns whether the new player experience is finished."""
        return self._new_player_experience_finished

    def is_leaderboard_anonymized(self) -> bool:
        """:class: `bool` Returns whether the leaderboard is anonymized."""
        return self._is_leaderboard_anonymized

    def is_act_rank_badge_hidden(self) -> bool:
        """:class: `bool` Returns whether the act rank badge is hidden."""
        return self._is_act_rank_badge_hidden

    def get_latest_competitive_update(self) -> Optional[LatestCompetitiveUpdate]:
        """:class: `LatestCompetitiveUpdate` Returns the latest competitive update."""
        return self._latest_competitive_update

    def get_latest_rank_tier(self, season_act: Optional[Season] = None) -> Optional[Tier]:
        """:class: `Tier` Returns the last rank tier."""
        if season_act is None:
            season_act = self._client.act

        competitive = self.queue_skills.competitive
        if competitive is None:
            return None

        seasonal_info = competitive.get_seasonal_info()
        if seasonal_info is None:
            return None

        for info in seasonal_info:
            if info.season == season_act:
                return info.tier

        return None

    def get_latest_competitive_season(self) -> Optional[SeasonalInfo]:
        """:class: `SeasonalInfo` Returns the latest competitive season."""
        if self.queue_skills.competitive is None:
            return None

        seasonal_info = self.queue_skills.competitive.get_seasonal_info()
        if seasonal_info is None:
            return None

        for si in seasonal_info:
            if si.season == self._client.season:
                return si

        return None
