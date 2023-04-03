from typing import Dict, Union

from .object import Object
from .response import Response


class Currency(Object):
    displayName: Union[str, Dict[str, str]]
    displayNameSingular: Union[str, Dict[str, str]]
    displayIcon: str
    largeIcon: str
    assetPath: str


Currencies = Response[Currency]
