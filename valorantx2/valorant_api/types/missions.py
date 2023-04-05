from typing import Dict, List, Optional, TypedDict, Union

from .object import Object
from .response import Response


class Objective(TypedDict):
    objectiveUuid: str
    value: int


class Mission(Object):
    displayName: Optional[Union[str, Dict[str, str]]]
    title: Optional[Union[str, Dict[str, str]]]
    type: Optional[str]
    xpGrant: int
    progressToComplete: int
    activationDate: str
    expirationDate: str
    tags: List[str]
    objectives: List[Objective]
    assetPath: str


Missions = Response[List[Mission]]
MissionUUID = Response[Mission]
