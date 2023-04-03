from typing import Dict, Union

from .object import Object
from .response import Response


class ContentTier(Object):
    displayName: Union[str, Dict[str, str]]
    devName: str
    rank: int
    juiceValue: int
    juiceCost: int
    highlightColor: str
    displayIcon: str
    assetPath: str


ContentTiers = Response[ContentTier]
