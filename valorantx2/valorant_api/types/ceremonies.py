from typing import Dict, Union

from .object import Object
from .response import Response


class Caremony(Object):
    displayName: Union[str, Dict[str, str]]
    assetPath: str


Ceremonies = Response[Caremony]
