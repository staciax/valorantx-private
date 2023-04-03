from typing import Dict, List, Optional, Union

from .object import Object
from .response import Response


class Level(Object):
    sprayLevel: int
    displayName: Union[str, Dict[str, str]]
    displayIcon: str
    assetPath: str


class Spray(Object):
    displayName: Union[str, Dict[str, str]]
    category: str
    themeUuid: str
    displayIcon: str
    fullIcon: Optional[str]
    fullTransparentIcon: Optional[str]
    animationPng: Optional[str]
    animationGif: Optional[str]
    assetPath: str
    levels: List[Level]


SprayLevel = Level
SprayLevels = Response[Level]
Sprays = Response[Spray]
