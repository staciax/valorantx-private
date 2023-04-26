from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Dict, List

from ..enums import PremierEventType, PremierMapSelectionStrategy, try_enum

if TYPE_CHECKING:
    from ..types.premiers import (
        Event as EventPayload,
        PremierSeason as PremierSeasonPayload,
        ScheduleConference as ScheduleConferencePayload,
        ScheduleDivision as ScheduleDivisionPayload,
    )

# fmt: off
__all__ = (
    'ScheduleDivision',
    'ScheduleConference',
    'Event',
    'PremierSeason',
)
# fmt: on


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


class Event:
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
        self.map_pool_map_ids: list[str] = data['MapPoolMapIDs']
        self.points_required_to_participate: int = data['PointsRequiredToParticipate']

    def __repr__(self) -> str:
        return f'<Event id={self.id!r} type={self.type!r}>'

    def __eq__(self, object: object) -> bool:
        return isinstance(object, Event) and object.id == self.id

    def __ne__(self, object: object) -> bool:
        return not self.__eq__(object)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def start_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_date_time)

    @property
    def end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._end_date_time)


class PremierSeason:
    def __init__(self, data: PremierSeasonPayload) -> None:
        self.id: str = data['ID']
        self.competitive_season_id: str = data['CompetitiveSeasonID']
        self._start_time: str = data['StartTime']
        self._end_time: str = data['EndTime']
        self.events: list[Event] = [Event(event) for event in data['Events']]
        self.championship_point_requirement: int = data['ChampionshipPointRequirement']
        self.championship_event_id: str = data['ChampionshipEventID']
        self.enrollment_phase_start_date_time: str = data['EnrollmentPhaseStartDateTime']
        self.enrollment_phase_end_date_time: str = data['EnrollmentPhaseEndDateTime']

    def __repr__(self) -> str:
        return f'<PremierSeason id={self.id!r}>'

    def __eq__(self, object: object) -> bool:
        return isinstance(object, PremierSeason) and object.id == self.id

    def __ne__(self, object: object) -> bool:
        return not self.__eq__(object)

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def start_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_time)

    @property
    def end_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._end_time)
