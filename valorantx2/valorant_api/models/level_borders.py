from __future__ import annotations

from typing import TYPE_CHECKING

from ..asset import Asset
from ..enums import ItemType
from .abc import BaseModel

if TYPE_CHECKING:
    from ..cache import CacheState
    from ..types.level_borders import LevelBorder as LevelBorderPayload

    # from typing_extensions import Self

# fmt: off
__all__ = (
    'LevelBorder',
)
# fmt: on


class LevelBorder(BaseModel):
    def __init__(self, state: CacheState, data: LevelBorderPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._starting_level: int = data['startingLevel']
        self._level_number_appearance: str = data['levelNumberAppearance']
        self._small_player_card_appearance: str = data['smallPlayerCardAppearance']
        self.asset_path: str = data['assetPath']
        self.type: ItemType = ItemType.level_border
        self._is_favorite = True

    def __repr__(self) -> str:
        return f'<LevelBorder starting_level={self.starting_level!r}>'

    def __lt__(self, other: object) -> bool:
        return isinstance(other, LevelBorder) and self.starting_level < other.starting_level

    def __le__(self, other: object) -> bool:
        return isinstance(other, LevelBorder) and self.starting_level <= other.starting_level

    def __gt__(self, other: object) -> bool:
        return isinstance(other, LevelBorder) and self.starting_level > other.starting_level

    def __ge__(self, other: object) -> bool:
        return isinstance(other, LevelBorder) and self.starting_level >= other.starting_level

    @property
    def starting_level(self) -> int:
        """:class: `int` Returns the starting level of the level border."""
        return self._starting_level

    @property
    def level_number_appearance(self) -> Asset:
        """:class: `Asset` Returns the level number appearance of the level border."""
        return Asset._from_url(state=self._state, url=self._level_number_appearance)

    @property
    def small_player_card_appearance(self) -> Asset:
        """:class: `Asset` Returns the small player card appearance of the level border."""
        return Asset._from_url(state=self._state, url=self._small_player_card_appearance)

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the level border with the given UUID."""
    #     data = client._assets.get_level_border(uuid=str(uuid))
    #     return cls(client=client, data=data) if data else None
