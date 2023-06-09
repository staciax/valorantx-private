from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, List, Optional

from ..enums import SeasonType, try_enum

if TYPE_CHECKING:
    from ..client import Client
    from ..types.content import Content as ContentPayload, Event as EventPayload, Season as SeasonPayload

# from .events import Event as _Event
# from .seasons import Season as _Season

__all__ = (
    'Content',
    'Event',
    'Season',
)


class Season:
    def __init__(self, data: SeasonPayload) -> None:
        self.id: str = data['ID']
        self.name: str = data['Name']
        self._start_time: str = data['StartTime']
        self._end_time: str = data['EndTime']
        self._is_active: bool = data['IsActive']
        self.type: SeasonType = try_enum(SeasonType, data['Type'])

    def is_active(self) -> bool:
        return self._is_active

    @property
    def start_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_time)

    @property
    def end_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._end_time)


class Event:
    def __init__(self, data: EventPayload) -> None:
        self.id: str = data['ID']
        self.name: str = data['Name']
        self._start_time: str = data['StartTime']
        self._end_time: str = data['EndTime']
        self._is_active: bool = data['IsActive']

    def is_active(self) -> bool:
        return self._is_active

    @property
    def start_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._start_time)

    @property
    def end_time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self._end_time)


class Content:
    def __init__(self, client: Client, data: ContentPayload) -> None:
        self._client: Client = client
        self.disabled_ids: List[str] = data['DisabledIDs']
        self.seasons: List[Season] = [Season(season) for season in data['Seasons']]
        self.events: List[Event] = [Event(event) for event in data['Events']]

    def get_season(self, season_id: str) -> Optional[Season]:
        for season in self.seasons:
            if season.id == season_id:
                return season
        return None

    def get_event(self, event_id: str) -> Optional[Event]:
        for event in self.events:
            if event.id == event_id:
                return event
        return None
