from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..enums import PremierEventType, PremierMapSelectionStrategy, try_enum
from ..models.user import User

# from valorantx2.types.user import PartialUser as PartialUserPayload


if TYPE_CHECKING:
    from ..client import Client
    from ..types.premiers import (
        Conference as ConferencePayload,
        Customization as CustomizationPayload,
        Eligibility as EligibilityPayload,
        Event as EventPayload,
        Player as PlayerPayload,
        RosterMember as RosterMemberPayload,
        RosterV2 as RosterPayload,
        ScheduleConference as ScheduleConferencePayload,
        ScheduleDivision as ScheduleDivisionPayload,
        Season as SeasonPayload,
    )

# fmt: off
__all__ = (
    'Conference',
    'Eligibility',
    'PremierEvent',
    'PremierSeason',
    'ScheduleDivision',
    'ScheduleConference',
    'Roster',
)
# fmt: on

# class Roster:
#     ...


class ScheduleDivision:
    def __init__(self, data: ScheduleDivisionPayload) -> None:
        self.division: int = data['Division']
        self.iso_start_date_time: str = data['StartDateTime']
        self.iso_end_date_time: str = data['EndDateTime']
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
        return datetime.datetime.fromisoformat(self.iso_start_date_time)

    @property
    def end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.iso_end_date_time)


class ScheduleConference:
    def __init__(self, data: ScheduleConferencePayload) -> None:
        self.conference: str = data['Conference']
        self.iso_start_date_time: str = data['StartDateTime']
        self.iso_end_date_time: str = data['EndDateTime']

    def __repr__(self) -> str:
        return f'<ScheduleConference conference={self.conference!r}>'

    @property
    def start_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.iso_start_date_time)

    @property
    def end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.iso_end_date_time)


class Event:
    def __init__(self, data: EventPayload) -> None:
        self.id: str = data['ID']
        self.type: PremierEventType = try_enum(PremierEventType, data['Type'])
        self.iso_start_date_time: str = data['StartDateTime']
        self.iso_end_date_time: str = data['EndDateTime']
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
        return datetime.datetime.fromisoformat(self.iso_start_date_time)

    @property
    def end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.iso_end_date_time)


class Season:
    def __init__(self, data: SeasonPayload) -> None:
        self.id: str = data['ID']
        self.competitive_season_id: str = data['CompetitiveSeasonID']
        self.iso_start_time: str = data['StartTime']
        self.iso_end_time: str = data['EndTime']
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
        return datetime.datetime.fromisoformat(self.iso_start_time)

    @property
    def end_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.iso_end_time)

    @property
    def enrollment_phase_start_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._enrollment_phase_start_date_time)

    @property
    def enrollment_phase_end_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._enrollment_phase_end_date_time)


class Eligibility:
    def __init__(self, data: EligibilityPayload) -> None:
        self.subject: str = data['subject']
        self.account_verification_status: bool = data['accountVerificationStatus']
        self.ranked_placement_completion_status: bool = data['rankedPlacementCompletionStatus']

    def __repr__(self) -> str:
        return f'<PremierEligibility subject={self.subject!r}>'


class Conference:
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

    async def fetch_roster(self) -> Roster:
        return await self._client.fetch_premier_roster(self.roster_id)


class RosterMember(User):
    def __init__(self, client: Client, data: RosterMemberPayload) -> None:
        super().__init__(client, data)
        self.role: str = data.get('role')
        self.role_id: int = data.get('roleId')
        self.raw_created_at: int = data.get('createdAt')

    @property
    def created_at(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.raw_created_at / 1000)


class Customization:
    def __init__(self, data: CustomizationPayload) -> None:
        self.icon_id: str = data['icon']
        self.raw_primary_color: str = data['primaryColor']  # (R=1.000000,G=0.473532,B=0.552012,A=1.000000)
        self.raw_secondary_color: str = data['secondaryColor']  # (R=0.323143,G=0.076185,B=0.008023,A=1.000000)
        self.raw_tertiary_color: str = data['tertiaryColor']  # (R=0.049707,G=0.048172,B=0.051269,A=1.000000)


class Roster:
    def __init__(self, client: Client, data: RosterPayload) -> None:
        self._client: Client = client
        self.id: str = data['rosterId']
        self.affinity: str = data['affinity']
        self.name: str = data['name']
        self.tag: str = data['tag']
        self._members: Dict[str, RosterMember] = {
            member['puuid']: RosterMember(self._client, member) for member in data['members']
        }
        self.customization: Customization = Customization(data['customization'])
        self.invites: List[Any] = data['invites']
        self.locks: List[Any] = data['locks']
        self.minimum_required_members_for_enrollment: int = data['minimumRequiredMembersForEnrollment']
        self.matches_since_reset: int = data['matchesSinceReset']
        self.tournaments_since_reset: int = data['tournamentsSinceReset']
        self.raw_updated_at: int = data['updatedAt']
        self.raw_created_at: int = data['createdAt']
        # try update members indetity
        # for member in self._members.values():
        # self._client.loop.create_task(member.update_identities())

    def __repr__(self) -> str:
        return f'<PremierRoster id={self.id!r} name={self.name!r} tag={self.tag!r}>'

    def get_member(self, puuid: str) -> Optional[RosterMember]:
        return self._members.get(puuid)

    @property
    def members(self) -> List[RosterMember]:
        return list(self._members.values())

    @property
    def created_at(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.raw_created_at / 1000)

    @property
    def updated_at(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.raw_updated_at / 1000)


PremierEvent = Event
PremierSeason = Season
