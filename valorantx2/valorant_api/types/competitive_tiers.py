from typing import Dict, List, TypedDict, Union

from .object import Object
from .response import Response


class Tier(TypedDict):
    tier: int
    tierName: Union[str, Dict[str, str]]
    division: str
    divisionName: Union[str, Dict[str, str]]
    color: str
    backgroundColor: str
    smallIcon: str
    largeIcon: str
    rankTriangleDownIcon: str
    rankTriangleUpIcon: str


class CompetitiveTier(Object):
    assetObjectName: str
    tiers: List[Tier]
    assetPath: str


CompetitiveTiers = Response[CompetitiveTier]
