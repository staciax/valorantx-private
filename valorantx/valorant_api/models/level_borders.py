from __future__ import annotations

from typing import TYPE_CHECKING

from ..asset import Asset
from ..enums import ItemType
from .abc import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..cache import CacheState
    from ..types.level_borders import LevelBorder as LevelBorderPayload

# fmt: off
__all__ = (
    'LevelBorder',
)
# fmt: on


class LevelBorder(BaseModel):
    def __init__(self, state: CacheState, data: LevelBorderPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self.starting_level: int = data['startingLevel']
        self._level_number_appearance: str = data['levelNumberAppearance']
        self._small_player_card_appearance: str = data['smallPlayerCardAppearance']
        self.asset_path: str = data['assetPath']
        self.type: ItemType = ItemType.level_border

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
    def level_number_appearance(self) -> Asset:
        """:class: `Asset` Returns the level number appearance of the level border."""
        return Asset._from_url(state=self._state, url=self._level_number_appearance)

    @property
    def small_player_card_appearance(self) -> Asset:
        """:class: `Asset` Returns the small player card appearance of the level border."""
        return Asset._from_url(state=self._state, url=self._small_player_card_appearance)

    @classmethod
    def _copy(cls, level_border: Self) -> Self:
        """Returns a copy of the level border."""
        self = cls.__new__(cls)  # bypass __init__
        self._state = level_border._state
        self.starting_level = level_border.starting_level
        self._level_number_appearance = level_border._level_number_appearance
        self._small_player_card_appearance = level_border._small_player_card_appearance
        self.asset_path = level_border.asset_path
        self.type = level_border.type
        return self

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the level border with the given UUID."""
    #     data = client._assets.get_level_border(uuid=str(uuid))
    #     return cls(client=client, data=data) if data else None
