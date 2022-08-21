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

from .base import BaseModel

from ..asset import Asset
from ..localization import Localization

from typing import Any, Dict, List, Optional, Union, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from ..client import Client

# fmt: off
__all__ = (
    'CompetitiveTier',
    'MMR'
)


# fmt: on]

class Tier:

    def __init__(self, client: Client, data: Any) -> None:
        self._client: Client = client
        self._update(data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Tier tier={self.tier!r} name={self.name!r} division={self.division!r}>'

    def __hash__(self) -> int:
        return hash(self.tier)

    def __eq__(self, other) -> bool:
        return isinstance(other, Tier) and self.tier == other.tier

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def _update(self, data: Any) -> None:
        self.tier: int = data['tier']
        self._name: Union[str, Dict[str, str]] = data['tierName']
        self._division: Optional[str] = data['division']
        self._division_name: Union[str, Dict[str, str]] = data['divisionName']
        self.color: str = data['color']
        self.background_color: str = data['backgroundColor']
        self._small_icon: Optional[str] = data['smallIcon']
        self._large_icon: Optional[str] = data['largeIcon']
        self._rank_triangle_down_icon: Optional[str] = data['rankTriangleDownIcon']
        self._rank_triangle_up_icon: Optional[str] = data['rankTriangleUpIcon']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the tier's names."""
        return Localization(self._name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the tier's name."""
        return self.name_localizations.american_english

    @property
    def division(self) -> Optional[str]:
        """:class: `str` Returns the tier's division."""
        return self._division.removeprefix('ECompetitiveDivision::') if self._division else None

    @property
    def division_name_localizations(self) -> Localization:
        """:class: `Localization` Returns the tier's division names."""
        return Localization(self._division_name, locale=self._client.locale)

    @property
    def division_name(self) -> str:
        """:class: `str` Returns the tier's division."""
        return self.division_name_localizations.american_english

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

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.asset_object_name

    def __repr__(self) -> str:
        return f'<CompetitiveTier asset_object_name={self.asset_object_name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self.asset_object_name: str = data['assetObjectName']
        self._tiers: List[Tier] = data['tiers']
        self.asset_path: str = data['assetPath']

    @property
    def tiers(self) -> List[Tier]:
        """:class: `list` Returns the competitive tier's tiers."""
        return [Tier(client=self._client, data=tier) for tier in self._tiers]

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the competitive tier with the given UUID."""
        data = client.assets.get_competitive_tier(uuid)
        return cls(client=client, data=data) if data else None

class CompetitiveUpdate(TypedDict):  # TODO: Model
    MatchID: str
    MapID: str
    SeasonID: str
    MatchStartTime: int
    TierAfterUpdate: int
    TierBeforeUpdate: int
    RankedRatingAfterUpdate: int
    RankedRatingBeforeUpdate: int
    RankedRatingEarned: int
    RankedRatingPerformanceBonus: int
    AFKPenalty: int

class MMR(BaseModel):

    def __init__(self, client: Client, data: Any, **kwargs) -> None:
        super().__init__(client, data, **kwargs)

    def __repr__(self) -> str:
        return f'<MMR uuid={self.uuid!r} version={self.version!r} latest_competitive_update={self.latest_competitive_update!r}>'

    def __hash__(self) -> int:
        return hash(self.uuid)

    def _update(self, data: Any) -> None:
        self._uuid = data['Subject']
        self.version = data['Version']
        self.queue_skills: Dict[str, Any] = data['QueueSkills']  # TODO: Object
        self.new_player_experience_finished: bool = data['NewPlayerExperienceFinished']
        self.is_leaderboard_anonymized: bool = data['IsLeaderboardAnonymized']
        self.is_act_rank_badge_hidden: bool = data['IsActRankBadgeHidden']
        self._latest_competitive_update: Dict[str, Any] = data['LatestCompetitiveUpdate']
        # TODO: Object
        self.latest_competitive_update: CompetitiveUpdate = CompetitiveUpdate(self._latest_competitive_update)
