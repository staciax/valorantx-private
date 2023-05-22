from __future__ import annotations

from typing import TYPE_CHECKING

from valorantx.valorant_api.models.player_titles import PlayerTitle as PlayerTitleValorantAPI

from .abc import Item

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.player_titles import PlayerTitle as PlayerTitlePayloadValorantAPI

    from ..valorant_api_cache import CacheState

# fmt: off
__all__ = (
    'PlayerTitle',
)
# fmt: on


class PlayerTitle(PlayerTitleValorantAPI, Item):
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
