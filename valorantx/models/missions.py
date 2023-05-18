from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

from valorantx.valorant_api.models.missions import Mission as MissionValorantAPI

from .. import utils

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.missions import Mission as MissionPayloadValorantAPI

    from ..types.contracts import Mission as MissionPayload, MissionMetadata as MissionMetadataPayload
    from ..valorant_api_cache import CacheState

# fmt: off
__all__ = (
    'Mission',
    'MissionMetadata',
)
# fmt: on


class Mission(MissionValorantAPI):
    def __init__(self, *, state: CacheState, data: MissionPayloadValorantAPI, data_mission: MissionPayload) -> None:
        super().__init__(state=state, data=data)
        self.id: str = data_mission['ID']
        self._is_complete: bool = data_mission['Complete']
        self._expiration_time: str = data_mission['ExpirationTime']
        self.current_progress: int = 0
        self.left_progress: int = 0
        self.total_progress: int = 0
        self._update(data=data_mission)

    def _update(self, data: MissionPayload) -> None:
        if self.objectives is not None:
            for obj in self.objectives:
                if obj.uuid in data['Objectives']:
                    # if self.progress_to_complete < obj.value:
                    #     self.current_progress = data['Objectives'][obj.uuid]
                    self.current_progress = data['Objectives'][obj.uuid]
                    self.left_progress = obj.value - self.current_progress
                    self.total_progress = obj.value

    @property
    def target(self) -> int:
        """:class: `int` Returns the mission's target."""
        return self.total_progress

    def is_completed(self) -> bool:
        """:class: `bool` Returns whether the mission is complete."""
        return self._is_complete

    @property
    def expiration_time(self) -> datetime.datetime:  # maybe optional?
        """:class: `datetime.datetime` Returns the contract's expiration time."""
        return utils.parse_iso_datetime(self._expiration_time)

    @classmethod
    def from_contract(cls, state: CacheState, data: MissionPayload) -> Optional[Self]:
        """Returns the mission with the given UUID."""
        mission = state.get_mission(uuid=data['ID'])
        if mission is None:
            return None
        return cls(state=state, data=mission._data, data_mission=data)


class MissionMetadata:
    def __init__(self, data: MissionMetadataPayload) -> None:
        self.npe_completed: bool = data['NPECompleted']
        self._weekly_check_point: str = data.get('WeeklyCheckpoint')
        self._weekly_refill_time: Optional[str] = data.get('WeeklyRefillTime')

    def __bool__(self) -> bool:
        return self.npe_completed

    def __repr__(self) -> str:
        attrs = [
            ('npe_completed', self.npe_completed),
            ('weekly_check_point', self.weekly_check_point),
            ('weekly_refill_time', self.weekly_refill_time),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MissionMetadata) and (
            self.npe_completed == other.npe_completed
            and self.weekly_check_point == other.weekly_check_point
            and self.weekly_refill_time == other.weekly_refill_time
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def weekly_check_point(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the weekly check point."""
        return utils.parse_iso_datetime(self._weekly_check_point)

    @property
    def weekly_refill_time(self) -> Optional[datetime.datetime]:
        """:class: `datetime.datetime` Returns the weekly refill time."""
        if self._weekly_refill_time is None:
            return None
        return utils.parse_iso_datetime(self._weekly_refill_time)
