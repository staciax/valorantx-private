from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from ..asset import Asset
from ..enums import Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..cache import CacheState
    from ..types.themes import Theme as ThemePayload

# fmt: off
__all__ = (
    'Theme',
)
# fmt: on


class Theme(BaseModel):
    def __init__(self, state: CacheState, data: ThemePayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self._store_featured_image: Optional[str] = data['storeFeaturedImage']
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Theme display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the ceremony's name."""
        return self._display_name_localized

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the ceremony's display icon."""
        if self._display_icon is None:
            return None
        return Asset._from_url(self._state, self._display_icon)

    @property
    def store_featured_image(self) -> Optional[Asset]:
        """:class: `Asset` Returns the ceremony's store featured image."""
        if self._store_featured_image is None:
            return None
        return Asset._from_url(self._state, self._store_featured_image)

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the theme with the given UUID."""
    #     data = client._assets.get_theme(uuid)
    #     return cls(client=client, data=data) if data else None
