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
from ..enums import Locale
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'Map',
)
# fmt: on


class Location:
    def __init__(self, data: Dict[str, float]) -> None:
        self.x: float = data['x']
        self.y: float = data['y']

    def __repr__(self) -> str:
        return f'<Location x={self.x} y={self.y}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Location) and self.x == other.x and self.y == other.y

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Callout:
    def __init__(self, client: Client, data: Dict[str, Any]) -> None:
        self._region_name: Dict[str, str] = data['regionName']
        self._super_region_name: Dict[str, str] = data['superRegionName']
        self.location: Location = Location(data['location'])
        self._region_name_localized: Localization = Localization(self._region_name, locale=client.locale)
        self._super_region_name_localized: Localization = Localization(self._super_region_name, locale=client.locale)

    def __str__(self) -> str:
        return self.region_name

    def __repr__(self) -> str:
        attrs = [
            ('region_name', self.region_name),
            ('super_region_name', self.super_region_name),
            ('location', self.location),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Callout) and self.region_name == other.region_name and self.location == other.location

    def region_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._region_name_localized.from_locale(locale)

    def super_region_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._super_region_name_localized.from_locale(locale)

    @property
    def region_name(self) -> str:
        return self._region_name_localized.locale

    @property
    def super_region_name(self) -> str:
        return self._super_region_name_localized.locale


class Map(BaseModel):
    def __init__(self, client: Client, data: Mapping[str, Any]) -> None:
        super().__init__(client=client, data=data)
        self._uuid: str = data['uuid']
        self._display_name: Dict[str, str] = data['displayName']
        self._coordinates: Dict[str, str] = data['coordinates']
        self._list_view_icon: Optional[str] = data['listViewIcon']
        self._splash: Optional[str] = data['splash']
        self.asset_path: str = data['assetPath']
        self.url: str = data['mapUrl']
        self.x_multiplier: float = data['xMultiplier']
        self.y_multiplier: float = data['yMultiplier']
        self.x_scalar_to_add: float = data['xScalarToAdd']
        self.y_scalar_to_add: float = data['yScalarToAdd']
        self.callouts: List[Callout] = [Callout(client, callout) for callout in data['callouts']]
        self._display_name_localized: Localization = Localization(self._display_name, locale=client.locale)
        self._coordinates_localized: Localization = Localization(self._coordinates, locale=client.locale)

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<Map display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    def coordinates_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._coordinates_localized.from_locale(locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the mission's name."""
        return self._display_name_localized.locale

    @property
    def coordinates(self) -> str:
        """:class: `str` Returns the mission's coordinates."""
        return self._coordinates_localized.locale

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

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the mission with the given UUID."""
        data = client._assets.get_map(uuid=uuid)
        return cls(client=client, data=data) if data else None
