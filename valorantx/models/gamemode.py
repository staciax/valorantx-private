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

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Union

from ..asset import Asset
from ..enums import GameModeType
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client
    from .weapons import Weapon

__all__ = (
    'GameMode',
    'GameModeEquippable',
)


class GameMode(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Dict[str, str] = data['displayName']
        self._allows_match_timeouts: bool = data.get('allowsMatchTimeouts', False)
        self._is_team_voice_allowed: bool = data.get('isTeamVoiceAllowed', False)
        self._is_minimap_hidden: bool = data.get('isMinimapHidden', False)
        self._orb_count: int = data.get('orbCount', 0)
        self._rounds_per_half: int = data.get('roundsPerHalf', -1)
        self._team_roles: Optional[List[str]] = data.get('teamRoles')
        self._game_feature_overrides: Optional[List[Dict[str, Any]]]
        self._game_rule_bool_overrides: Optional[List[Dict[str, Any]]]
        self._display_icon: Optional[str] = data.get('displayIcon')
        self.asset_path: str = data['assetPath']

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<GameMode display_name={self.display_name!r}>'

    def __eq__(self, other: Union[GameMode, GameModeType]) -> bool:
        if isinstance(other, GameMode):
            return self.uuid == other.uuid
        return self.uuid == str(other)

    def __ne__(self, other: Union[GameMode, GameModeType]) -> bool:
        return not self.__eq__(other)

    # def __contains__(self, item: Union[GameMode, GameModeType]) -> bool:
    #     ...

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the game mode's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the game mode's name."""
        return self.name_localizations.american_english

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the game mode's display icon."""
        if self._display_icon is None:
            return None
        return Asset(self._client, self._display_icon)

    def allows_match_timeouts(self) -> bool:
        """:class: `bool` Returns whether the game mode allows match timeouts."""
        return self._allows_match_timeouts

    def is_team_voice_allowed(self) -> bool:
        """:class: `bool` Returns whether the game mode allows team voice."""
        return self._is_team_voice_allowed

    def is_minimap_hidden(self) -> bool:
        """:class: `bool` Returns whether the game mode hides the minimap."""
        return self._is_minimap_hidden

    @property
    def orb_count(self) -> int:
        """:class: `int` Returns the game mode's orb count."""
        return self._orb_count

    @property
    def rounds_per_half(self) -> int:
        """:class: `int` Returns the game mode's rounds per half."""
        return self._rounds_per_half

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the game mode with the given UUID."""
        data = client._assets.get_game_mode(uuid)
        return cls(client=client, data=data) if data else None


class GameModeEquippable(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Dict[str, str] = data['displayName']
        self._category: Optional[str] = data['category']
        self._display_icon: str = data['displayIcon']
        self._kill_stream_icon: str = data['killStreamIcon']
        self.asset_path: str = data['assetPath']

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<GameModeEquippable display_name={self.display_name!r}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the game mode's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the game mode's name."""
        return self.name_localizations.american_english

    @property
    def category(self) -> Optional[str]:
        """:class: `str` Returns the game mode's category."""
        return self._category.removeprefix('EEquippableCategory::') if self._category else None

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the game mode's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def kill_stream_icon(self) -> Asset:
        """:class: `Asset` Returns the game mode's kill stream icon."""
        return Asset._from_url(client=self._client, url=self._kill_stream_icon)

    @property
    def get_weapon(self) -> Weapon:
        """:class: `Weapon` Returns the game mode's weapon."""
        data = self._client._assets.get_weapon(uuid=self._uuid)
        return Weapon(client=self._client, data=data)

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the game mode with the given UUID."""
        data = client._assets.get_game_mode_equippable(uuid)
        return cls(client=client, data=data) if data else None
