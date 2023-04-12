from __future__ import annotations

from typing import TYPE_CHECKING

from ..valorant_api.models.bundles import Bundle as BundleValorantAPI
from .abc import _Cost

if TYPE_CHECKING:
    from ..valorant_api.types.bundles import Bundle as BundleValorantAPIPayload
    from ..valorant_api_cache import CacheState


class Bundle(BundleValorantAPI, _Cost):
    def __init__(self, state: CacheState, data: BundleValorantAPIPayload) -> None:
        super().__init__(state=state, data=data)
