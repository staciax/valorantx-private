from typing import Dict, Union

from .object import Object
from .response import Response


class Event(Object):
    displayName: Union[str, Dict[str, str]]
    shortDisplayName: Union[str, Dict[str, str]]
    startTime: str
    endTime: str
    assetPath: str


Events = Response[Event]
