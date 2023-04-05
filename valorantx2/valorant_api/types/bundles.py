from typing import Dict, List, Union

from .object import Object
from .response import Response


class Bundle(Object):
    displayName: Union[str, Dict[str, str]]
    displayNameSubText: Union[str, Dict[str, str]]
    description: Union[str, Dict[str, str]]
    extraDescription: Union[str, Dict[str, str]]
    promoDescription: Union[str, Dict[str, str]]
    useAdditionalContext: bool
    displayIcon: str
    displayIcon2: str
    verticalPromoImage: str
    assetPath: str


Bundles = Response[List[Bundle]]
BundleUUID = Response[Bundle]

# TODO: BundleItem
