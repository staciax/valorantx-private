from typing import Any, Dict, List, Optional, TypedDict


class MatchOutcome(TypedDict):
    MatchID: str
    TeamID: str
    Outcome: str
    GameWins: int


class Origin(TypedDict):
    Type: str
    Slot: int


class Player(TypedDict):
    ID: str
    SummonerName: str
    FirstName: str
    LastName: str
    Image: str
    Status: str


class Record(TypedDict):
    Wins: int
    Losses: int
    Ties: int


class HomeLeague(TypedDict):
    ID: str
    Name: str
    ImageURL: str
    Region: str


class Team(TypedDict):
    ID: str
    Name: str
    Code: str
    ImageURL: str
    AlternativeImageURL: str
    BackgroundImageURL: str
    MatchOutcome: MatchOutcome
    Origin: Origin
    Players: Optional[List[Player]]
    Record: Record
    HomeLeague: HomeLeague


class Game(TypedDict):
    ID: str
    Number: int
    VODs: List[Any]


class Match(TypedDict):
    ID: str
    StartTime: str
    StageName: str
    Stage: str
    Status: str  # unstarted
    Teams: List[Team]
    Games: Optional[List[Game]]
    Streams: Optional[Any]


class ScheduleLeague(TypedDict):
    LeagueID: str
    LeagueName: str
    TournamentID: str
    TournamentName: str
    TournamentState: str
    StartTime: str
    Matches: List[Match]


class Teams(TypedDict):
    Teams: List[Team]


class Bracket(TypedDict):
    Stage: str
    Type: str  # upper, lower, final
    RoundNumber: int
    Matches: List[Match]


class StandingBracket(TypedDict):
    Columns: Optional[Any]
    UpperBracket: List[Any]
    LowerBracket: List[Any]
    Final: Optional[Any]


class Standing(TypedDict):
    Group: Optional[Any]
    Bracket: StandingBracket


class TournamentSection(TypedDict):
    ID: str
    LeagueID: str
    Name: str
    StageName: str
    Type: str  # bracket
    Standing: Standing


class TournamentStanding(TypedDict):
    ID: str
    Name: str
    StartTime: str
    EndTime: str
    TournamentSections: Dict[str, TournamentSection]


class TournamentStandings(TypedDict):
    TournamentStandings: List[TournamentStanding]
