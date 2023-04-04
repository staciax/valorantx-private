# from typing import TypedDict
from typing import Dict, List, Optional, Union

from .object import Object
from .response import Response


class Level(Object):
    charmLevel: int
    displayName: Union[str, Dict[str, str]]
    displayIcon: str
    assetPath: str


class Buddy(Object):
    displayName: Union[str, Dict[str, str]]
    isHiddenIfNotOwned: bool
    themeUuid: Optional[str]
    displayIcon: str
    assetPath: str
    levels: List[Level]


BuddyLevel = Level
Buddies = Response[Buddy]
