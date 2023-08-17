from __future__ import annotations

from typing import TYPE_CHECKING, List

from valorant.models.sprays import Spray as SprayValorantAPI, SprayLevel as SprayLevelValorantAPI

from .abc import BundleItemOffer, Item

if TYPE_CHECKING:
    from typing_extensions import Self
    from valorant.types.sprays import Spray as SprayPayloadValorantAPI, SprayLevel as SprayLevelPayloadValorantAPI

    from ..types.store import BundleItemOffer as BundleItemOfferPayload
    from ..valorant_api_cache import CacheState


__all__ = (
    'Spray',
    'SprayBundle',
    'SprayLevel',
)


class Spray(SprayValorantAPI, Item):
    if TYPE_CHECKING:
        _state: CacheState

    def __init__(self, *, state: CacheState, data: SprayPayloadValorantAPI, favorite: bool = False) -> None:
        self._data = data
        super().__init__(state=state, data=data)
        Item.__init__(self)
        self.levels: List[SprayLevel] = [SprayLevel(state=state, data=level, parent=self) for level in data['levels']]
        self._is_favorite: bool = favorite

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, spray: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = spray._uuid
        self._state = spray._state
        self._data = spray._data.copy()
        self._display_name = spray._display_name
        self.category = spray.category
        self.theme_uuid = spray.theme_uuid
        self._is_null_spray = spray._is_null_spray
        self._display_icon = spray._display_icon
        self._full_icon = spray._full_icon
        self._full_transparent_icon = spray._full_transparent_icon
        self._animation_png = spray._animation_png
        self._animation_gif = spray._animation_gif
        self.asset_path = spray.asset_path
        self.levels = spray.levels.copy()
        self._display_name_localized = spray._display_name_localized
        self._cost = spray._cost
        return self

    @classmethod
    def from_loadout(cls, *, spray: Self, favorite: bool) -> Self:
        self = spray._copy(spray)
        self._is_favorite = favorite
        return self


class SprayLevel(SprayLevelValorantAPI):
    parent: Spray

    def __init__(self, *, state: CacheState, data: SprayLevelPayloadValorantAPI, parent: Spray) -> None:
        self._data = data
        super().__init__(state=state, data=data, parent=parent)

    # helpers

    @property
    def cost(self) -> int:
        return self.parent.cost

    @property
    def price(self) -> int:
        return self.cost

    @classmethod
    def _copy(cls, spray_level: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = spray_level._uuid
        self._state = spray_level._state
        self._data = spray_level._data.copy()
        self.spray_level = spray_level.spray_level
        self._display_name = spray_level._display_name
        self._display_icon = spray_level._display_icon
        self.asset_path = spray_level.asset_path
        self.parent = spray_level.parent._copy(spray_level.parent)
        self._display_name_localized = spray_level._display_name_localized
        return self


class SprayBundle(Spray, BundleItemOffer):
    def __init__(
        self,
        *,
        state: CacheState,
        data: SprayPayloadValorantAPI,
        data_bundle: BundleItemOfferPayload,
    ) -> None:
        Spray.__init__(self, state=state, data=data)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<SprayBundle display_name={self.display_name!r}>'

    @classmethod
    def from_bundle(cls, *, spray: Spray, data: BundleItemOfferPayload) -> Self:
        spray = spray._copy(spray)
        return cls(state=spray._state, data=spray._data, data_bundle=data)
