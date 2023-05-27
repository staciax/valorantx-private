from __future__ import annotations

from typing import TYPE_CHECKING

from valorantx.valorant_api.models.player_cards import PlayerCard as PlayerCardValorantAPI

from .abc import BundleItemOffer, Item

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.player_cards import PlayerCard as PlayerCardPayloadValorantAPI
    from valorantx.valorant_api_cache import CacheState

    from ..types.store import BundleItemOffer as BundleItemOfferPayload

__all__ = (
    'PlayerCard',
    'PlayerCardBundle',
)


class PlayerCard(PlayerCardValorantAPI, Item):
    if TYPE_CHECKING:
        _state: CacheState

    def __init__(self, *, state: CacheState, data: PlayerCardPayloadValorantAPI, favorite: bool = False) -> None:
        super().__init__(state=state, data=data)
        Item.__init__(self)
        self._is_favorite: bool = favorite

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, player_card: Self) -> Self:
        self = super()._copy(player_card)
        self._cost = player_card._cost
        self._is_favorite = player_card._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, player_card: Self, favorite: bool = False) -> Self:
        self = player_card._copy(player_card)
        self._is_favorite = favorite
        return self


class PlayerCardBundle(PlayerCard, BundleItemOffer):
    def __init__(
        self, *, state: CacheState, data: PlayerCardPayloadValorantAPI, data_bundle: BundleItemOfferPayload
    ) -> None:
        PlayerCard.__init__(self, state=state, data=data)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<PlayerCardBundle display_name={self.display_name!r}>'

    @classmethod
    def from_bundle(cls, *, player_card: PlayerCard, data: BundleItemOfferPayload) -> Self:
        plyaer_card = player_card._copy(player_card)
        return cls(state=plyaer_card._state, data=plyaer_card._data, data_bundle=data)
