"""
The MIT License (MIT)

Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional

from ..asset import Asset
from ..enums import ItemType
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'LevelBorder',
)
# fmt: on


class LevelBorder(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
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
        return Asset._from_url(client=self._client, url=self._level_number_appearance)

    @property
    def small_player_card_appearance(self) -> Asset:
        """:class: `Asset` Returns the small player card appearance of the level border."""
        return Asset._from_url(client=self._client, url=self._small_player_card_appearance)

    def is_favorite(self) -> bool:
        """:class: `bool` Returns whether or not the level border is favorited."""
        return self._is_favorite

    def to_favorite(self) -> None:
        """Makes the level border a favorite."""
        self._is_favorite = True

    async def add_favorite(self, *, force: bool = False) -> bool:
        """coro Adds the skin to the user's favorites."""

        if self.is_favorite() and not force:
            return False
        to_fav = await self._client.add_favorite(self)
        if self in to_fav._level_borders:
            self._is_favorite = True
        return self.is_favorite()

    async def remove_favorite(self, *, force: bool = False) -> bool:
        """coro Removes the skin from the user's favorites."""
        if not self.is_favorite() and not force:
            return False
        remove_fav = await self._client.remove_favorite(self)
        if self not in remove_fav._level_borders:
            self._is_favorite = False
        return self.is_favorite()

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the level border with the given UUID."""
        data = client._assets.get_level_border(uuid=str(uuid))
        return cls(client=client, data=data) if data else None
