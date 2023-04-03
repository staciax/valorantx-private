from typing import Dict, List, TypedDict, Union

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
    freeRewards: List[Reward]


class Content(TypedDict):
    relationType: str
    relationUuid: str
    chapters: List[Chapter]
    premiumRewardScheduleUuid: str
    premiumVPCost: int


class Contract(Object):
    displayName: Union[str, Dict[str, str]]
    displayIcon: str
    shipIt: bool
    freeRewardScheduleUuid: str
    content: Content
    assetPath: str


Contracts = Response[Contract]
