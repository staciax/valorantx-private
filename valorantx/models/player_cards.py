from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from valorantx.valorant_api.models.player_cards import PlayerCard as PlayerCardValorantAPI

from .abc import BundleItemOffer, Item

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.player_cards import PlayerCard as PlayerCardPayloadValorantAPI
    from valorantx.valorant_api_cache import CacheState

    from ..types.store import BundleItemOffer as BundleItemOfferPayload


class PlayerCard(PlayerCardValorantAPI, Item):
    def __init__(self, *, state: CacheState, data: PlayerCardPayloadValorantAPI) -> None:
        super().__init__(state=state, data=data)
        Item.__init__(self)


class PlayerCardBundle(PlayerCard, BundleItemOffer):
    def __init__(
        self, *, state: CacheState, data: PlayerCardPayloadValorantAPI, data_bundle: BundleItemOfferPayload
    ) -> None:
        PlayerCard.__init__(self, state=state, data=data)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<PlayerCardBundle display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bundle: BundleItemOfferPayload) -> Optional[Self]:
        player_card = state.get_player_card(data_bundle['BundleItemOfferID'])
        if player_card is None:
            return None
        return cls(state=state, data=player_card._data, data_bundle=data_bundle)
