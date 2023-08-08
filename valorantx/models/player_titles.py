from __future__ import annotations

from typing import TYPE_CHECKING

from valorant.models.player_titles import PlayerTitle as PlayerTitleValorantAPI

from .abc import BundleItemOffer, Item

if TYPE_CHECKING:
    from typing_extensions import Self
    from valorant.types.player_titles import PlayerTitle as PlayerTitlePayloadValorantAPI

    from ..types.store import BundleItemOffer as BundleItemOfferPayload
    from ..valorant_api_cache import CacheState

# fmt: off
__all__ = (
    'PlayerTitle',
    'PlayerTitleBundle',
)
# fmt: on


class PlayerTitle(PlayerTitleValorantAPI, Item):
    if TYPE_CHECKING:
        _state: CacheState

    def __init__(self, *, state: CacheState, data: PlayerTitlePayloadValorantAPI, favorite: bool = False) -> None:
        super().__init__(state=state, data=data)
        Item.__init__(self)
        self._is_favorite: bool = favorite  # not supported favorite

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, player_title: Self) -> Self:
        self = super()._copy(player_title)
        self._cost = player_title._cost
        self._is_favorite = player_title._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, player_title: Self, favorite: bool = False) -> Self:
        self = player_title._copy(player_title)
        self._is_favorite = favorite
        return self


class PlayerTitleBundle(PlayerTitle, BundleItemOffer):
    def __init__(
        self, *, state: CacheState, data: PlayerTitlePayloadValorantAPI, data_bundle: BundleItemOfferPayload
    ) -> None:
        PlayerTitle.__init__(self, state=state, data=data)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<PlayerCardBundle display_name={self.display_name!r}>'

    @classmethod
    def from_bundle(cls, *, player_title: PlayerTitle, data: BundleItemOfferPayload) -> Self:
        player_title = player_title._copy(player_title)
        return cls(state=player_title._state, data=player_title._data, data_bundle=data)
