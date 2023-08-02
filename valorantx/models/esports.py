from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..asset import Asset

if TYPE_CHECKING:
    from ..client import Client
    from ..types.esports import (
        Bracket as BracketPayload,
        Game as GamePayload,
        HomeLeague as HomeLeaguePayload,
        Match as MatchPayload,
        Player as PlayerPayload,
        Record as RecordPayload,
        ScheduleForLeague as ScheduleForLeaguePayload,
        Standing as StandingPayload,
        StandingBracket as StandingBracketPayload,
        Team as TeamPayload,
        TournamentSection as TournamentSectionPayload,
        TournamentStanding as TournamentStandingPayload,
    )


class Player:
    def __init__(self, team: Team, data: PlayerPayload) -> None:
        self._team: Team = team
        self.id: str = data['ID']
        self.summoner_name: str = data['SummonerName']
        self.first_name: str = data['FirstName']
        self.last_name: str = data['LastName']
        self._image: str = data['Image']
        self._default_image: str = 'https://static.lolesports.com/players/download.png'
        self.status: str = data['Status']

    def __repr__(self) -> str:
        return f'<Player id={self.id} summoner_name={self.summoner_name} first_name={self.first_name} last_name={self.last_name}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Player) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def team(self) -> Team:
        return self._team

    @property
    def image(self) -> Optional[Asset]:
        if self._image == self._default_image:
            return None
        return Asset._from_url(self._team._client, self._image)

    @property
    def default_image(self) -> Asset:
        return Asset._from_url(self._team._client, self._default_image)


class Record:
    def __init__(self, data: RecordPayload) -> None:
        self.wins: int = data['Wins']
        self.losses: int = data['Losses']
        self.ties: int = data['Ties']

    def __repr__(self) -> str:
        return f'<Record wins={self.wins} losses={self.losses} ties={self.ties}>'

    @property
    def winrate(self) -> float:
        return self.wins / (self.wins + self.losses)


class HomeLeague:
    def __init__(self, client: Client, data: HomeLeaguePayload) -> None:
        self._client: Client = client
        self.id: str = data['ID']
        self.name: str = data['Name']
        self._image_url: str = data['ImageURL']
        self.region: str = data['Region']

    def __repr__(self) -> str:
        return f'<HomeLeague id={self.id} name={self.name} region={self.region}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, HomeLeague) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def image(self) -> Optional[Asset]:
        if self._image_url == '':
            return None
        return Asset._from_url(self._client, self._image_url)


class Team:
    def __init__(self, client: Client, data: TeamPayload) -> None:
        self._client: Client = client
        self.id: str = data['ID']
        self.name: str = data['Name']
        self.code: str = data['Code']
        self._image_url: str = data['ImageURL']
        self._alternative_image_url: str = data['AlternativeImageURL']
        self._background_image_url: str = data['BackgroundImageURL']
        # self.MatchOutcome: Optional[Any] = data['MatchOutcome']
        # self.Origin: str = data['Origin']
        self._players: Dict[str, Player] = {}
        if data['Players'] is not None:
            self._players: Dict[str, Player] = {player['ID']: Player(self, player) for player in data['Players']}
        self.record: Record = Record(data['Record'])
        self.home_league: HomeLeague = HomeLeague(client, data['HomeLeague'])

    def __repr__(self) -> str:
        return f'<Team id={self.id} name={self.name} code={self.code}>'

    @property
    def players(self) -> List[Player]:
        return list(self._players.values())

    @property
    def image(self) -> Optional[Asset]:
        if self._alternative_image_url == '':
            return None
        return Asset._from_url(self._client, self._alternative_image_url)

    @property
    def background_image(self) -> Optional[Asset]:
        if self._background_image_url == '':
            return None
        return Asset._from_url(self._client, self._background_image_url)

    def get_player(self, player_id: str) -> Optional[Player]:
        return self._players.get(player_id)


class Game:
    def __init__(self, data: GamePayload) -> None:
        self.id: str = data['ID']
        self.number: int = data['Number']
        self.vods: List[Any] = data['VODs']


class Match:
    def __init__(self, client: Client, data: MatchPayload, schedule: Optional[ScheduleForLeague] = None) -> None:
        self._client: Client = client
        self._schedule: Optional[ScheduleForLeague] = schedule
        self.id: str = data['ID']
        self.start_time_iso: str = data['StartTime']
        self.stage_name: str = data['StageName']
        self.stage: str = data['Stage']
        self.status: str = data['Status']
        self._teams: Dict[str, Team] = {team['ID']: Team(client, team) for team in data['Teams']}
        self.games: Optional[List[Game]] = None
        if data['Games'] is not None:
            self.games = [Game(game) for game in data['Games']]
        self.streams: Optional[Any] = data['Streams']

    def __repr__(self) -> str:
        return f'<Match id={self.id} start_time_iso={self.start_time_iso} status={self.status}>'

    @property
    def teams(self) -> List[Team]:
        return list(self._teams.values())

    def get_team(self, team_id: str) -> Optional[Team]:
        return self._teams.get(team_id)


class ScheduleForLeague:
    def __init__(self, client: Client, data: ScheduleForLeaguePayload) -> None:
        self._client: Client = client
        self.league_id: str = data['LeagueID']
        self.league_name: str = data['LeagueName']
        self.tournament_id: str = data['TournamentID']
        self.tournament_name: str = data['TournamentName']
        self.tournament_state: str = data['TournamentState']
        self.start_time_iso: str = data['StartTime']
        self._matches: Dict[str, Match] = {match['ID']: Match(client, match, self) for match in data['Matches']}
        self._teams: Dict[str, Team] = {}

    def __repr__(self) -> str:
        return f'<ScheduleForLeague league_id={self.league_id} league_name={self.league_name} tournament_id={self.tournament_id} tournament_name={self.tournament_name} start_time_iso={self.start_time_iso}>'

    @property
    def matches(self) -> List[Match]:
        return list(self._matches.values())

    @property
    def teams(self) -> List[Team]:
        return list(self._teams.values())

    def get_match(self, match_id: str) -> Optional[Match]:
        return self._matches.get(match_id)

    def get_team(self, team_id: str) -> Optional[Team]:
        return self._teams.get(team_id)

    async def refresh_teams(self) -> None:
        data = await self._client.http.get_esport_teams_for_league(self.league_id, self.tournament_id)
        self._teams = {team['ID']: Team(self._client, team) for team in data['Teams']}


class Bracket:
    def __init__(self, client: Client, data: BracketPayload) -> None:
        self._client: Client = client
        self.stage: str = data['Stage']
        self.type: str = data['Type']
        self.round_number: int = data['RoundNumber']
        self._matches: Dict[str, Match] = {match['ID']: Match(client, match) for match in data['Matches']}

    def __repr__(self) -> str:
        return f'<Bracket stage={self.stage} type={self.type} round_number={self.round_number}>'

    @property
    def matches(self) -> List[Match]:
        return list(self._matches.values())

    def get_match(self, match_id: str) -> Optional[Match]:
        return self._matches.get(match_id)


class StandingBracket:
    def __init__(self, client: Client, data: StandingBracketPayload) -> None:
        self._client: Client = client
        self.columns: Optional[Any] = data['Columns']
        self.upper_bracket: List[Bracket] = [Bracket(client, bracket) for bracket in data['UpperBracket']]
        self.lower_bracket: List[Bracket] = [Bracket(client, bracket) for bracket in data['LowerBracket']]
        self.final: Optional[Any] = data['Final']

    def __repr__(self) -> str:
        return f'<StandingBracket>'


class Standing:
    def __init__(self, client: Client, data: StandingPayload) -> None:
        self._client: Client = client
        self.group: Optional[Any] = data['Group']
        self.bracket: StandingBracket = StandingBracket(client, data['Bracket'])

    def __repr__(self) -> str:
        return f'<Standing>'


class TournamentSection:
    def __init__(self, client: Client, data: TournamentSectionPayload) -> None:
        self._client: Client = client
        self.id: str = data['ID']
        self.league_id: str = data['LeagueID']
        self.name: str = data['Name']
        self.stage_name: str = data['StageName']
        self.type: str = data['Type']
        self.standing: Standing = Standing(client, data['Standing'])

    def __repr__(self) -> str:
        return f'<TournamentSection id={self.id} name={self.name} stage_name={self.stage_name} type={self.type}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TournamentSection) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class TournamentStanding:
    def __init__(self, client: Client, data: TournamentStandingPayload) -> None:
        self._client: Client = client
        self.id: str = data['ID']
        self.name: str = data['Name']
        self.start_time_iso: str = data['StartTime']
        self.end_time_iso: str = data['EndTime']
        self._sections: Dict[str, TournamentSection] = {
            section: TournamentSection(client, data) for section, data in data['TournamentSections'].items()
        }

    def __repr__(self) -> str:
        return f'<TournamentStanding id={self.id} name={self.name} start_time_iso={self.start_time_iso} end_time_iso={self.end_time_iso}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TournamentStanding) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def sections(self) -> List[TournamentSection]:
        return list(self._sections.values())

    def get_section(self, section_id: str) -> Optional[TournamentSection]:
        return self._sections.get(section_id)

    @property
    def start_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.start_time_iso)

    @property
    def end_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.end_time_iso)
