from typing import Dict, Union

from .object import Object
from .response import Response


class Ceremony(Object):
    displayName: Union[str, Dict[str, str]]
    assetPath: str


Ceremonies = Response[Ceremony]
