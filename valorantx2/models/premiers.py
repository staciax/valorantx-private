from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from ..enums import PremierEventType, PremierMapSelectionStrategy, try_enum
from ..models.user import User

if TYPE_CHECKING:
    from ..client import Client
    from ..types.premiers import (
        Conference as ConferencePayload,
        Eligibility as EligibilityPayload,
        Event as EventPayload,
        Player as PlayerPayload,
        ScheduleConference as ScheduleConferencePayload,
        ScheduleDivision as ScheduleDivisionPayload,
        Season as SeasonPayload,
    )

# fmt: off
__all__ = (
    'PremierConference',
    'PremierEligibility',
    'PremierEvent',
    'PremierSeason',
    'PremierPleyer',
    'ScheduleDivision',
    'ScheduleConference',
)
# fmt: on

# class Roster:
#     ...


class ScheduleDivision:
    def __init__(self, data: ScheduleDivisionPayload) -> None:
        self.division: int = data['Division']
        self._start_date_time: str = data['StartDateTime']
        self._end_date_time: str = data['EndDateTime']
        self.queue_id: str = data['QueueID']
        self.required_max_league_points: str = data['RequiredMaxLeaguePoints']

    def __repr__(self) -> str:
        return f'<ScheduleDivision division={self.division}>'

    def __int__(self) -> int:
        return self.division

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ScheduleDivision) and other.division == self.division

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.division)

    @property
    def start_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_date_time)

    @property
    def end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._end_date_time)


class ScheduleConference:
    def __init__(self, data: ScheduleConferencePayload) -> None:
        self.conference: str = data['Conference']
        self._start_date_time: str = data['StartDateTime']
        self._end_date_time: str = data['EndDateTime']

    def __repr__(self) -> str:
        return f'<ScheduleConference conference={self.conference!r}>'

    @property
    def start_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_date_time)

    @property
    def end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._end_date_time)


class PremierEvent:
    def __init__(self, data: EventPayload) -> None:
        self.id: str = data['ID']
        self.type: PremierEventType = try_enum(PremierEventType, data['Type'])
        self._start_date_time: str = data['StartDateTime']
        self._end_date_time: str = data['EndDateTime']
        self.schedule_per_division: List[ScheduleDivision] = [
            ScheduleDivision(schedule) for schedule in data['SchedulePerDivision']
        ]
        self.schedule_per_conference: Dict[str, ScheduleConference] = {
            conference: ScheduleConference(data['SchedulePerConference'][conference])
            for conference in data['SchedulePerConference']
        }
        self.map_selection_strategy: PremierMapSelectionStrategy = try_enum(
            PremierMapSelectionStrategy, data['MapSelectionStrategy']
        )
        self.map_pool_map_ids: List[str] = data['MapPoolMapIDs']
        self.points_required_to_participate: int = data['PointsRequiredToParticipate']

    def __repr__(self) -> str:
        return f'<Event id={self.id!r} type={self.type!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PremierEvent) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def schedule_per_conferences(self) -> List[ScheduleConference]:
        return list(self.schedule_per_conference.values())

    @property
    def start_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_date_time)

    @property
    def end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._end_date_time)


class PremierSeason:
    def __init__(self, data: SeasonPayload) -> None:
        self.id: str = data['ID']
        self.competitive_season_id: str = data['CompetitiveSeasonID']
        self._start_time: str = data['StartTime']
        self._end_time: str = data['EndTime']
        self.events: List[PremierEvent] = [PremierEvent(event) for event in data['Events']]
        self.championship_point_requirement: int = data['ChampionshipPointRequirement']
        self.championship_event_id: str = data['ChampionshipEventID']
        self._enrollment_phase_start_date_time: str = data['EnrollmentPhaseStartDateTime']
        self._enrollment_phase_end_date_time: str = data['EnrollmentPhaseEndDateTime']

    def __repr__(self) -> str:
        return f'<PremierSeason id={self.id!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PremierSeason) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def start_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_time)

    @property
    def end_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._end_time)

    @property
    def enrollment_phase_start_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._enrollment_phase_start_date_time)

    @property
    def enrollment_phase_end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._enrollment_phase_end_date_time)


class PremierEligibility:
    def __init__(self, data: EligibilityPayload) -> None:
        self.subject: str = data['subject']
        self.account_verification_status: bool = data['accountVerificationStatus']
        self.ranked_placement_completion_status: bool = data['rankedPlacementCompletionStatus']

    def __repr__(self) -> str:
        return f'<PremierEligibility subject={self.subject!r}>'


class PremierConference:
    def __init__(self, data: ConferencePayload) -> None:
        self.id: str = data['id']
        self.key: str = data['key']
        self.game_pods: List[str] = data['gamePods']
        self.timezone: str = data['timezone']

    def __repr__(self) -> str:
        return f'<PremierConference id={self.id!r} key={self.key!r}>'


class PremierPleyer(User):
    def __init__(self, client: Client, data: PlayerPayload) -> None:
        super().__init__(client, data=data)
        self.roster_id: str = data['rosterId']
        self.invites: List[Any] = data['invites']
        self.version: int = data['version']
        self.created_at: int = data['createdAt']
        self.updated_at: int = data['updatedAt']

    def __repr__(self) -> str:
        return f'<PremierPlayer puuid={self.puuid!r} roster_id={self.roster_id!r} riot_id={self.roster_id!r}>'
