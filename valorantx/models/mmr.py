from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..client import Client
    from ..types.mmr import (
        LatestCompetitiveUpdate as LatestCompetitiveUpdatePayload,
        MatchmakingRating as MatchmakingRatingPayload,
        QueueSkill as QueueSkillPayload,
        QueueSkills as QueueSkillsPayload,
        SeasonalInfo as SeasonalInfoPayload,
    )
    from .competitive_tiers import Tier
    from .maps import Map
    from .match import MatchDetails
    from .seasons import CompetitiveSeason, Season


__all__ = (
    'MatchmakingRating',
    'QueueSkill',
    'QueueSkills',
    'SeasonalInfo',
    'LatestCompetitiveUpdate',
)


class LatestCompetitiveUpdate:
    def __init__(self, client: Client, data: LatestCompetitiveUpdatePayload) -> None:
        self._client: Client = client
        self.match_id: str = data['MatchID']
        self.map_id: str = data['MapID']
        self.season_id: str = data['SeasonID']
        self.match_start_time: int = data['MatchStartTime']
        self.tier_after_update: int = data['TierAfterUpdate']
        self.tier_before_update: int = data['TierBeforeUpdate']
        self.ranked_rating_after_update: int = data['RankedRatingAfterUpdate']
        self.ranked_rating_before_update: int = data['RankedRatingBeforeUpdate']
        self.ranked_rating_earned: int = data['RankedRatingEarned']
        self.ranked_rating_performance_bonus: int = data['RankedRatingPerformanceBonus']
        self.competitive_movement: str = data['CompetitiveMovement']
        self.afk_penalty: int = data['AFKPenalty']

    def __repr__(self) -> str:
        return f'<LatestCompetitiveUpdate season_id={self.season_id!r} map_id={self.map_id!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LatestCompetitiveUpdate) and self.match_id == other.match_id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def get_map(self) -> Optional[Map]:
        """:class: `Map` Returns the map."""
        # TODO: implement this
        # to_uuid = MapType.from_url(self._map_id)
        # return self._client.get_map(uuid=to_uuid)

    def get_season(self) -> Optional[Season]:
        """:class: `Season` Returns the season."""
        return self._client.valorant_api.get_season(self.season_id)

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
        return self._client.valorant_api.get_season(uuid=self.season_id)

    def get_tier(self) -> Optional[Tier]:
        """:class: `Tier` Returns the tier."""

        competitive_season: Optional[CompetitiveSeason] = None

        competitive_season = self._client.valorant_api.get_competitive_season_season_id(self.season_id)
        if competitive_season is None:
            return None

        if competitive_season.competitive_tiers is None:
            return None

        for tier in competitive_season.competitive_tiers.tiers:
            if tier.tier == self.competitive_tier_number:
                return tier

        # return None


class QueueSkill:
    def __init__(self, client: Client, data: QueueSkillPayload) -> None:
        self._client: Client = client
        self.total_games_needed_for_rating: int = data['TotalGamesNeededForRating']
        self.total_games_needed_for_leaderboard: int = data['TotalGamesNeededForLeaderboard']
        self.current_season_games_needed_for_rating: int = data['CurrentSeasonGamesNeededForRating']
        self._seasonal_info_list: Dict[str, Any] = data['SeasonalInfoBySeasonID']

    # def __repr__(self) -> str:
    #     attrs = [
    #         ('total_games_needed_for_rating', self.total_games_needed_for_rating),
    #         ('total_games_needed_for_leaderboard', self.total_games_needed_for_leaderboard),
    #         ('current_season_games_needed_for_rating', self.current_season_games_needed_for_rating),
    #     ]
    #     joined = ' '.join('%s=%r' % t for t in attrs)
    #     return f'<{self.__class__.__name__} {joined}>'

    def get_seasonal_info(self) -> Optional[List[SeasonalInfo]]:
        """:class: `list` Returns the seasonal info."""

        if self._seasonal_info_list is None:
            return None

        return [SeasonalInfo(client=self._client, data=seasonal_info) for seasonal_info in self._seasonal_info_list.values()]


class QueueSkills:
    def __init__(self, client: Client, data: QueueSkillsPayload) -> None:
        self._client: Client = client
        self.competitive: Optional[QueueSkill] = None
        self.custom: Optional[QueueSkill] = None
        self.deathmatch: Optional[QueueSkill] = None
        self.ggteam: Optional[QueueSkill] = None
        self.newmap: Optional[QueueSkill] = None
        self.onefa: Optional[QueueSkill] = None
        self.seeding: Optional[QueueSkill] = None
        self.snowball: Optional[QueueSkill] = None
        self.spikerush: Optional[QueueSkill] = None
        self.unrated: Optional[QueueSkill] = None
        if 'competitive' in data:
            self.competitive = QueueSkill(client=self._client, data=data['competitive'])
        if 'custom' in data:
            self.custom = QueueSkill(client=self._client, data=data['custom'])
        if 'deathmatch' in data:
            self.deathmatch = QueueSkill(client=self._client, data=data['deathmatch'])
        if 'ggteam' in data:
            self.ggteam = QueueSkill(client=self._client, data=data['ggteam'])
        if 'newmap' in data:
            self.newmap = QueueSkill(client=self._client, data=data['newmap'])
        if 'onefa' in data:
            self.onefa = QueueSkill(client=self._client, data=data['onefa'])
        if 'seeding' in data:
            self.seeding = QueueSkill(client=self._client, data=data['seeding'])
        if 'snowball' in data:
            self.snowball = QueueSkill(client=self._client, data=data['snowball'])
        if 'spikerush' in data:
            self.spikerush = QueueSkill(client=self._client, data=data['spikerush'])
        if 'unrated' in data:
            self.unrated = QueueSkill(client=self._client, data=data['unrated'])

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


class MatchmakingRating:
    def __init__(self, client: Client, data: MatchmakingRatingPayload) -> None:
        self._client: Client = client
        self.subject: str = data['Subject']
        self.version: int = data['Version']
        self._queue_skills: QueueSkills = QueueSkills(client, data['QueueSkills'])
        self._new_player_experience_finished: bool = data['NewPlayerExperienceFinished']
        self._is_leaderboard_anonymized: bool = data['IsLeaderboardAnonymized']
        self._is_act_rank_badge_hidden: bool = data['IsActRankBadgeHidden']
        self._latest_competitive_update: Optional[LatestCompetitiveUpdate] = LatestCompetitiveUpdate(
            client=self._client, data=data['LatestCompetitiveUpdate']
        )

    def __repr__(self) -> str:
        return f'<MMR subject={self.subject!r} version={self.version!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MatchmakingRating) and self.subject == other.subject and self.version == other.version

    def __hash__(self) -> int:
        return hash((self.subject, self.version))

    def new_player_experience_finished(self) -> bool:
        """:class: `bool` Returns whether the new player experience is finished."""
        return self._new_player_experience_finished

    def is_leaderboard_anonymized(self) -> bool:
        """:class: `bool` Returns whether the leaderboard is anonymized."""
        return self._is_leaderboard_anonymized

    def is_act_rank_badge_hidden(self) -> bool:
        """:class: `bool` Returns whether the act rank badge is hidden."""
        return self._is_act_rank_badge_hidden

    @property
    def queue_skills(self) -> QueueSkills:
        """:class: `QueueSkills` Returns the queue skills."""
        return self._queue_skills

    @property
    def latest_competitive_update(self) -> Optional[LatestCompetitiveUpdate]:
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
                return info.get_tier()

        return None
