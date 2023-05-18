from typing import Dict, List, Optional, TypedDict, Union

from .object import Object
from .response import Response


class Reward(Object):
    type: str
    amount: int
    isHighlighted: bool


class Level(TypedDict):
    reward: Reward
    xp: int
    vpCost: int
    isPurchasableWithVP: bool


class Chapter(TypedDict):
    isEpilogue: bool
    levels: List[Level]
    freeRewards: Optional[List[Reward]]


class Content(TypedDict):
    relationType: Optional[str]
    relationUuid: Optional[str]
    chapters: List[Chapter]
    premiumRewardScheduleUuid: Optional[str]
    premiumVPCost: int


class Contract(Object):
    displayName: Union[str, Dict[str, str]]
    displayIcon: Optional[str]
    shipIt: bool
    freeRewardScheduleUuid: str
    content: Content
    assetPath: str


Contracts = Response[List[Contract]]
ContractUUID = Response[Contract]
