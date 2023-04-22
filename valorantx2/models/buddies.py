from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from valorantx2.valorant_api.models.buddies import Buddy as BuddyValorantAPI, BuddyLevel as BuddyLevelValorantAPI

from .abc import BundleItemOffer, Item

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.store import BundleItemOffer as BundleItemOfferPayload
    from ..valorant_api.types.buddies import Buddy as BuddyPayload, BuddyLevel as BuddyLevelPayloadValorantAPI
    from ..valorant_api_cache import CacheState


class Buddy(BuddyValorantAPI, Item):
    def __init__(self, *, state: CacheState, data: BuddyPayload) -> None:
        super().__init__(state=state, data=data)
        Item.__init__(self)
        self.levels: List[BuddyLevel] = [BuddyLevel(state=state, data=level, parent=self) for level in data['levels']]


class BuddyLevel(BuddyLevelValorantAPI['Buddy'], Item):
    def __init__(self, *, state: CacheState, data: BuddyLevelPayloadValorantAPI, parent: Buddy) -> None:
        super().__init__(state=state, data=data, parent=parent)
        Item.__init__(self)


class BuddyLevelBundle(BuddyLevel, BundleItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: BuddyLevelPayloadValorantAPI,
        parent: Buddy,
        data_bundle: BundleItemOfferPayload,
    ) -> None:
        BuddyLevel.__init__(self, state=state, data=data, parent=parent)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<BuddyLevelBundle display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bundle: BundleItemOfferPayload) -> Optional[Self]:
        buddy = state.get_buddy_level(data_bundle['BundleItemOfferID'])
        if buddy is None:
            return None
        return cls(state=state, data=buddy._data, parent=buddy.parent, data_bundle=data_bundle)
