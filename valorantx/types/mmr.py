from typing import TYPE_CHECKING, Dict, List, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class SeasonInfo(TypedDict):
    SeasonID: str
    NumberOfWins: int
    NumberOfWinsWithPlacements: int
    NumberOfGames: int
    Rank: int
    CapstoneWins: int
    LeaderboardRank: int
    CompetitiveTier: int
    RankedRating: int
    WinsByTier: Dict[str, int]
    GamesNeededForRating: int
    TotalWinsNeededForRank: int


class QueueSkill(TypedDict):
    TotalGamesNeededForRating: int
    TotalGamesNeededForLeaderboard: int
    CurrentSeasonGamesNeededForRating: int
    SeasonalInfoBySeasonID: Dict[str, SeasonInfo]


class QueueSkills(TypedDict):
    competitive: NotRequired[QueueSkill]
    custom: NotRequired[QueueSkill]
    deathmatch: NotRequired[QueueSkill]
    ggteam: NotRequired[QueueSkill]
    newmap: NotRequired[QueueSkill]
    onefa: NotRequired[QueueSkill]
    seeding: NotRequired[QueueSkill]
    snowball: NotRequired[QueueSkill]
    spikerush: NotRequired[QueueSkill]
    swiftplay: NotRequired[QueueSkill]
    unrated: NotRequired[QueueSkill]


class LatestCompetitiveUpdate(TypedDict):
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
    CompetitiveMovement: str
    AFKPenalty: int


class MatchmakingRating(TypedDict):
    Version: int
    Subject: str
    NewPlayerExperienceFinished: bool
    # QueueSkills: QueueSkills
    LatestCompetitiveUpdate: LatestCompetitiveUpdate
    IsLeaderboardAnonymized: bool
    IsActRankBadgeHidden: bool


class TierDetail(TypedDict):
    rankedRatingThreshold: int
    startingPage: int
    startingIndex: int


class LeaderboardPlayer(TypedDict):
    PlayerCardID: str
    TitleID: str
    IsBanned: bool
    IsAnonymized: bool
    puuid: str
    gameName: str
    tagLine: str
    leaderboardRank: int
    rankedRating: int
    numberOfWins: int
    competitiveTier: int


class Leaderboards(TypedDict):
    Deployment: str
    QueueID: str
    SeasonID: str
    Players: List[LeaderboardPlayer]
    totalPlayers: int
    immortalStartingPage: int
    immortalStartingIndex: int
    topTierRRThreshold: int
    tierDetails: Dict[str, TierDetail]
    startIndex: int
    query: str


class PlayerCompetitiveUpdates(TypedDict):
    Version: int
    Subject: str
    Matches: List[LatestCompetitiveUpdate]
