from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ..valorant_api.models.player_cards import PlayerCard as PlayerCardValorantAPI
from .abc import BundleItemOffer, _Cost

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..types.store import ItemOffer as ItemOfferPayload
    from ..valorant_api.types.player_cards import PlayerCard as PlayerCardPayloadValorantAPI
    from ..valorant_api_cache import CacheState


class PlayerCard(PlayerCardValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: PlayerCardPayloadValorantAPI) -> None:
        super().__init__(state=state, data=data)


class PlayerCardBundle(PlayerCard, BundleItemOffer):
    def __init__(self, *, state: CacheState, data: PlayerCardPayloadValorantAPI, data_bundle: ItemOfferPayload) -> None:
        PlayerCard.__init__(self, state=state, data=data)
        BundleItemOffer.__init__(self, data=data_bundle)

    def __repr__(self) -> str:
        return f'<PlayerCardBundle display_name={self.display_name!r}>'

    @classmethod
    def from_data(cls, *, state: CacheState, data_bundle: ItemOfferPayload) -> Optional[Self]:
        player_card = state.get_player_card(data_bundle['BundleItemOfferID'])
        if player_card is None:
            return None
        return cls(state=state, data=player_card._data, data_bundle=data_bundle)
