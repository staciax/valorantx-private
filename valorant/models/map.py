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

from .base import BaseModel

from ..asset import Asset
from ..localization import Localization

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from ..client import Client

# fmt: off
__all__ = (
    'Map',
)
# fmt: on

class Map(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Map name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._coordinates: Union[str, Dict[str, str]] = data['coordinates']
        self._list_view_icon: Optional[str] = data['listViewIcon']
        self._splash: Optional[str] = data['splash']
        self.asset_path: str = data['assetPath']
        self.url: str = data['mapUrl']
        self.x_multiplier: float = data['xMultiplier']
        self.y_multiplier: float = data['yMultiplier']
        self.x_scalar_to_add: float = data['xScalarToAdd']
        self.y_scalar_to_add: float = data['yScalarToAdd']
        self._callouts: List[Dict[str, Any]] = data['callouts']  # TODO: Callout object

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the mission's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the mission's name."""
        return self.name_localizations.american_english

    @property
    def coordinate_localizations(self) -> Localization:
        """:class: `Localization` Returns the mission's coordinates."""
        return Localization(self._coordinates, locale=self._client.locale)

    @property
    def coordinates(self) -> str:
        """:class: `str` Returns the mission's coordinates."""
        return self.coordinate_localizations.american_english

    @property
    def list_view_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the mission's list view icon."""
        if self._list_view_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._list_view_icon)

    @property
    def splash(self) -> Optional[Asset]:
        """:class: `Asset` Returns the mission's splash."""
        if self._splash is None:
            return None
        return Asset._from_url(client=self._client, url=self._splash)

    @property
    def callouts(self) -> List[Dict[str, Any]]:
        """:class: `List[Dict[str, Any]]` Returns the mission's callouts."""
        return self._callouts

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the mission with the given UUID."""
        data = client.assets.get_map(uuid=uuid)
        return cls(client=client, data=data) if data else None
