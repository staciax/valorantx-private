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

from ..asset import Asset
from ..localization import Localization
from .base import BaseModel

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

# fmt: off
__all__ = (
    'Agent',
)
# fmt: on

# https://dash.valorant-api.com/endpoints/agents

class _AgentRole(BaseModel):

    def __init__(self, client: Client, data: Any) -> None:
        super().__init__(client=client, data=data)

    def _update(self, data: Any) -> None:
        self._uuid = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent role's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the agent role's name."""
        return self.name_localizations.american_english

    @property
    def description_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent role's descriptions."""
        return Localization(self._description, locale=self._client.locale)

    @property
    def description(self) -> str:
        """:class: `str` Returns the agent role's description."""
        return self.description_localizations.american_english

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the agent role's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

class Agent(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Agent name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._description: Union[str, Dict[str, str]] = data['description']
        self.developer_name: str = data['developerName']
        self.character_tags: Optional[str] = data['characterTags']
        self._display_icon: str = data['displayIcon']
        self._display_icon_small: str = data['displayIconSmall']
        self._bust_portrait: Optional[str] = data['bustPortrait']
        self._full_portrait: Optional[str] = data['fullPortrait']
        self._full_portrait_v2: Optional[str] = data['fullPortraitV2']
        self._killfeed_portrait: str = data['killfeedPortrait']
        self.background: Optional[str] = data['background']
        self.background_gradient_colors: List[str] = data['backgroundGradientColors']
        self.is_full_portrait_right_facing: bool = data['isFullPortraitRightFacing']
        self.is_playable_character: bool = data['isPlayableCharacter']
        self.is_available_for_test: bool = data['isAvailableForTest']
        self.is_base_content: bool = data['isBaseContent']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the agent's name."""
        return self.name_localizations.american_english

    @property
    def description_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's descriptions."""
        return Localization(self._description, locale=self._client.locale)

    @property
    def description(self) -> str:
        """:class: `str` Returns the agent's description."""
        return self.description_localizations.american_english

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the agent's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def display_icon_small(self) -> Asset:
        """:class: `Asset` Returns the agent's display icon small."""
        return Asset._from_url(client=self._client, url=self._display_icon_small)

    @property
    def bust_portrait(self) -> Optional[Asset]:
        """:class: `Asset` Returns the agent's bust portrait."""
        return Asset._from_url(client=self._client, url=self._bust_portrait) if self._bust_portrait else None

    @property
    def full_portrait(self) -> Optional[Asset]:
        """:class: `Asset` Returns the agent's full portrait."""
        return Asset._from_url(client=self._client, url=self._full_portrait) if self._full_portrait else None

    @property
    def full_portrait_v2(self) -> Optional[Asset]:
        """:class: `Asset` Returns the agent's full portrait v2."""
        return Asset._from_url(client=self._client, url=self._full_portrait_v2) if self._full_portrait_v2 else None

    @property
    def killfeed_portrait(self) -> Asset:
        """:class: `Asset` Returns the agent's killfeed portrait."""
        return Asset._from_url(client=self._client, url=self._killfeed_portrait)
