from typing import Dict, List, TypedDict, Union

from .object import Object
from .response import Response


class Location(TypedDict):
    x: float
    y: float


class Callout(TypedDict):
    regionName: Union[str, Dict[str, str]]
    superRegionName: Union[str, Dict[str, str]]
    location: Location


class Map(Object):
    displayName: Union[str, Dict[str, str]]
    coordinates: Union[str, Dict[str, str]]
    displayIcon: str
    listViewIcon: str
    splash: str
    assetPath: str
    mapUrl: str
    xMultiplier: float
    yMultiplier: float
    xScalarToAdd: float
    yScalarToAdd: float
    callouts: List[Callout]


Maps = Response[List[Map]]
MapUUID = Response[Map]
