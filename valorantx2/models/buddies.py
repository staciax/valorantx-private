from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ..valorant_api.models.buddies import Buddy as BuddyValorantAPI, BuddyLevel as BuddyLevelValorantAPI
from .abc import BundleItemOffer, _Cost

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.store import ItemOffer as ItemOfferPayload
    from ..valorant_api.types.buddies import Buddy as BuddyPayload, BuddyLevel as BuddyLevelPayloadValorantAPI
    from ..valorant_api_cache import CacheState


class Buddy(BuddyValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: BuddyPayload) -> None:
        super().__init__(state=state, data=data)


class BuddyLevel(BuddyLevelValorantAPI['Buddy'], _Cost):
    def __init__(self, *, state: CacheState, data: BuddyLevelPayloadValorantAPI, parent: Buddy) -> None:
        super().__init__(state=state, data=data, parent=parent)


class BuddyLevelBundle(BuddyLevel, BundleItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: BuddyLevelPayloadValorantAPI,
        parent: Buddy,
        data_bundle: ItemOfferPayload,
    ) -> None:
        BuddyLevel.__init__(self, state=state, data=data, parent=parent)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<BuddyLevelBundle display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bundle: ItemOfferPayload) -> Optional[Self]:
        buddy = state.get_buddy_level(data_bundle['BundleItemOfferID'])
        if buddy is None:
            return None
        return cls(state=state, data=buddy._data, parent=buddy.parent, data_bundle=data_bundle)
