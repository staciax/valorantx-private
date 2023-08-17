from __future__ import annotations

from typing import TYPE_CHECKING, List

from valorant.models.buddies import Buddy as BuddyValorantAPI, BuddyLevel as BuddyLevelValorantAPI

from .abc import BundleItemOffer, Item

if TYPE_CHECKING:
    from typing_extensions import Self
    from valorant.types.buddies import Buddy as BuddyPayload, BuddyLevel as BuddyLevelPayloadValorantAPI

    from ..types.store import BundleItemOffer as BundleItemOfferPayload
    from ..valorant_api_cache import CacheState

__all__ = (
    'Buddy',
    'BuddyLevel',
    'BuddyLevelBundle',
)


class Buddy(BuddyValorantAPI, Item):
    if TYPE_CHECKING:
        _state: CacheState

    def __init__(self, *, state: CacheState, data: BuddyPayload, favorite: bool = False) -> None:
        super().__init__(state=state, data=data)
        Item.__init__(self)
        self.levels: List[BuddyLevel] = [BuddyLevel(state=state, data=level, parent=self) for level in data['levels']]
        self._is_favorite: bool = favorite

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, buddy: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = buddy._uuid
        self._state = buddy._state
        self._display_name = buddy._display_name
        self._is_hidden_if_not_owned = buddy._is_hidden_if_not_owned
        self.theme_uuid = buddy.theme_uuid
        self._display_icon = buddy._display_icon
        self.asset_path = buddy.asset_path
        self.levels = buddy.levels.copy()
        self._name_localized = buddy._name_localized
        self._is_favorite = buddy._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, buddy: Self, favorite: bool) -> Self:
        self = buddy._copy(buddy)
        self._is_favorite = favorite
        return self


class BuddyLevel(BuddyLevelValorantAPI, Item):
    parent: Buddy
    _state: CacheState

    def __init__(self, *, state: CacheState, data: BuddyLevelPayloadValorantAPI, parent: Buddy) -> None:
        self._data = data
        super().__init__(state=state, data=data, parent=parent)
        Item.__init__(self)

    @classmethod
    def _copy(cls, buddy_level: Self) -> Self:
        """Creates a copy of the given buddy level."""
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = buddy_level._uuid
        self._state = buddy_level._state
        self.charm_level = buddy_level.charm_level
        self._display_name = buddy_level._display_name
        self._display_icon = buddy_level._display_icon
        self.asset_path = buddy_level.asset_path
        self.parent = buddy_level.parent._copy(buddy_level.parent)
        self._display_name_localized = buddy_level._display_name_localized
        return self


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
    def from_bundle(cls, *, buddy_level: BuddyLevel, data: BundleItemOfferPayload) -> Self:
        buddy_level = buddy_level._copy(buddy_level)
        return cls(state=buddy_level._state, data=buddy_level._data, parent=buddy_level.parent, data_bundle=data)

    # @classmethod
    # def from_data(cls, *, state: CacheState, data_bundle: BundleItemOfferPayload) -> Optional[Self]:
    #     buddy = state.get_buddy_level(data_bundle['BundleItemOfferID'])
    #     if buddy is None:
    #         return None
    #     return cls(state=state, data=buddy._data, parent=buddy.parent, data_bundle=data_bundle)
