from typing import Dict, Union

from .object import Object
from .response import Response


class PlayerCard(Object):
    displayName: Union[str, Dict[str, str]]
    isHiddenIfNotOwned: bool
    themeUuid: str
    displayIcon: str
    smallArt: str
    wideArt: str
    largeArt: str
    assetPath: str


PlayerCards = Response[PlayerCard]
