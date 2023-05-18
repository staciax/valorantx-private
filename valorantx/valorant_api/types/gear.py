from typing import Dict, List, Union

from .object import Object, ShopData
from .response import Response


class Gear_(Object):
    displayName: Union[str, Dict[str, str]]
    description: Union[str, Dict[str, str]]
    displayIcon: str
    assetPath: str
    shopData: ShopData


Gear = Response[List[Gear_]]
GearUUID = Response[Gear_]
