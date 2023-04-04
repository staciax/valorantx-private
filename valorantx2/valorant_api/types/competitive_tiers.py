from typing import Dict, List, Optional, TypedDict, Union

from .object import Object
from .response import Response


class Tier(TypedDict):
    tier: int
    tierName: Union[str, Dict[str, str]]
    division: str
    divisionName: Union[str, Dict[str, str]]
    color: str
    backgroundColor: str
    smallIcon: Optional[str]
    largeIcon: Optional[str]
    rankTriangleDownIcon: Optional[str]
    rankTriangleUpIcon: Optional[str]


class CompetitiveTier(Object):
    assetObjectName: str
    tiers: List[Tier]
    assetPath: str


CompetitiveTiers = Response[CompetitiveTier]
