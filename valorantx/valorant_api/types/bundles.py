from typing import Dict, List, Optional, Union

from .object import Object
from .response import Response


class Bundle(Object):
    displayName: Union[str, Dict[str, str]]
    displayNameSubText: Optional[Union[str, Dict[str, str]]]
    description: Union[str, Dict[str, str]]
    extraDescription: Optional[Union[str, Dict[str, str]]]
    promoDescription: Optional[Union[str, Dict[str, str]]]
    useAdditionalContext: bool
    displayIcon: str
    displayIcon2: str
    verticalPromoImage: str
    assetPath: str


Bundles = Response[List[Bundle]]
BundleUUID = Response[Bundle]

# TODO: BundleItem
