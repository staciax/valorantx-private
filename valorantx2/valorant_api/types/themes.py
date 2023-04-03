from typing import Dict, Optional, Union

from .object import Object
from .response import Response


class Theme(Object):
    displayName: Union[str, Dict[str, str]]
    displayIcon: Optional[str]
    storeFeaturedImage: Optional[str]
    assetPath: str


Themes = Response[Theme]
