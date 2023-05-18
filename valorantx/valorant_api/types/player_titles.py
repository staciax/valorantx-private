from typing import Dict, List, Union

from .object import Object
from .response import Response


class PlayerTitle(Object):
    displayName: Union[str, Dict[str, str]]
    titleText: Union[str, Dict[str, str]]
    isHiddenIfNotOwned: bool
    assetPath: str


PlayerTitles = Response[List[PlayerTitle]]
PlayerTitleUUID = Response[PlayerTitle]
