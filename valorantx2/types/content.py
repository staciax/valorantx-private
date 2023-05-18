from typing import Any, List, TypedDict


class Event(TypedDict):
    ID: str
    Name: str
    StartTime: str
    EndTime: str
    IsActive: bool


class Season(Event):
    Type: str


class Content(TypedDict):
    DisabledIDs: List[Any]
    Seasons: List[Season]
    Events: List[Any]
