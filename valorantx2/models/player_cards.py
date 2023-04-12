from __future__ import annotations

from typing import TYPE_CHECKING

from ..valorant_api.models.player_cards import PlayerCard as PlayerCardValorantAPI
from .abc import _Cost

if TYPE_CHECKING:
    from ..valorant_api.types.player_cards import PlayerCard as PlayerCardPayloadValorantAPI
    from ..valorant_api_cache import CacheState


class PlayerCard(PlayerCardValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: PlayerCardPayloadValorantAPI) -> None:
        super().__init__(state=state, data=data)
