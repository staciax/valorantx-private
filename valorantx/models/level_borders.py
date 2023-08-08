from __future__ import annotations

from typing import TYPE_CHECKING

from valorant.models.level_borders import LevelBorder as LevelBorderValorantAPI

if TYPE_CHECKING:
    from typing_extensions import Self
    from valorant.types.level_borders import LevelBorder as LevelBorderPayloadValorantAPI

    from ..valorant_api_cache import CacheState

# fmt: off
__all__ = (
    'LevelBorder',
)
# fmt: on


class LevelBorder(LevelBorderValorantAPI):
    def __init__(self, state: CacheState, data: LevelBorderPayloadValorantAPI, favorite: bool = False) -> None:
        super().__init__(state=state, data=data)
        self._is_favorite: bool = favorite

    def is_favorite(self) -> bool:
        return self._is_favorite

    @classmethod
    def _copy(cls, level_border: Self) -> Self:
        self = super()._copy(level_border)
        self._is_favorite = level_border._is_favorite
        return self

    @classmethod
    def from_loadout(cls, *, level_border: Self, favorite: bool = False) -> Self:
        self = level_border._copy(level_border)
        self._is_favorite = favorite
        return self
