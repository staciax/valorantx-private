from typing import Dict, List, Literal, TypedDict


class ScheduleDivision(TypedDict):
    Division: int
    StartDateTime: str
    EndDateTime: str
    QueueID: str
    RequiredMaxLeaguePoints: str


class ScheduleConference(TypedDict):
    Conference: str
    StartDateTime: str
    EndDateTime: str


class Event(TypedDict):
    ID: str
    Type: Literal["LEAGUE", "TOURNAMENT"]
    StartDateTime: str
    EndDateTime: str
    SchedulePerDivision: List[ScheduleDivision]
    SchedulePerConference: Dict[str, ScheduleConference]
    MapSelectionStrategy: Literal["RANDOM", "PICKBAN"]
    MapPoolMapIDs: List[str]
    PointsRequiredToParticipate: int


class Season(TypedDict):
    ID: str
    CompetitiveSeasonID: str
    StartTime: str
    EndTime: str
    Events: List[Event]
    ChampionshipPointRequirement: int
    ChampionshipEventID: str
    EnrollmentPhaseStartDateTime: str
    EnrollmentPhaseEndDateTime: str


class Seasons(TypedDict):
    PremierSeasons: List[Season]


class Eligibility(TypedDict):
    subject: str
    accountVerificationStatus: bool
    rankedPlacementCompletionStatus: bool


class Player(TypedDict):
    puuid: str
    rosterId: str
    invites: List
    version: int
    createdAt: int
    updatedAt: int


class Conference(TypedDict):
    id: str
    key: str
    gamePods: List[str]
    timezone: str


class Conferences(TypedDict):
    PremierConferences: List[Conference]
