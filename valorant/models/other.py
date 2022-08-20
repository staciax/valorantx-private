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

from typing import Any, Dict, NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

__all__ = (
    'MMR',
)

class CompetitiveUpdate(NamedTuple):  # TODO: Model
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

