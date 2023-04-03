from typing import Dict, TypedDict, Union

from .object import Object
from .response import Response


class GridPosition(TypedDict):
    row: int
    column: int


class ShopData(TypedDict):
    cost: int
    category: str
    categoryText: Union[str, Dict[str, str]]
    gridPosition: GridPosition
    canBeTrashed: bool
    image: str
    newImage: str
    newImage2: str
    assetPath: str


class Gear_(Object):
    displayName: Union[str, Dict[str, str]]
    description: Union[str, Dict[str, str]]
    displayIcon: str
    assetPath: str
    shopData: ShopData


Gear = Response[Gear_]
