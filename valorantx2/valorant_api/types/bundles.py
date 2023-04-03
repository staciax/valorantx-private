from typing import Dict, Union

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


Bundles = Response[Bundle]

# TODO: BundleItem
# TODO: Check Optional fields
