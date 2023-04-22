from __future__ import annotations

from typing import TYPE_CHECKING

from valorantx2.valorant_api.models.player_titles import PlayerTitle as PlayerTitleValorantAPI

from .abc import Item

if TYPE_CHECKING:
    from valorantx2.valorant_api.types.player_titles import PlayerTitle as PlayerTitlePayloadValorantAPI

    from ..valorant_api_cache import CacheState

# fmt: off
__all__ = (
    'PlayerTitle',
)
# fmt: on


class PlayerTitle(PlayerTitleValorantAPI, Item):
    def __init__(self, *, state: CacheState, data: PlayerTitlePayloadValorantAPI) -> None:
        super().__init__(state=state, data=data)
        Item.__init__(self)
