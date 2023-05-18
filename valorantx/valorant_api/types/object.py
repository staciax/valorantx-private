from typing import Dict, TypedDict, Union


class Object(TypedDict):
    uuid: str


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
