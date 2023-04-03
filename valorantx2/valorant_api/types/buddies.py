# from typing import TypedDict
from typing import Dict, List, Union

from .object import Object
from .response import Response


class Level(Object):
    charmLevel: int
    displayName: Union[str, Dict[str, str]]
    displayIcon: str
    assetPath: str


class Buddy(Object):
    displayName: str
    isHiddenIfNotOwned: bool
    themeUuid: str
    displayIcon: str
    assetPath: str
    levels: List[Level]


SprayLevel = Level
Buddies = Response[Buddy]
