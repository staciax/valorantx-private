from __future__ import annotations

# import datetime
from typing import TYPE_CHECKING, Dict, Optional, Union

from ...enums import Locale  # SeasonType, try_enum
from ..asset import Asset
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..cache import CacheState
    from ..types.content_tiers import ContentTier as ContentTierPayload

# fmt: off
__all__ = (
    'ContentTier',
)
# fmt: on


class ContentTier(BaseModel):
    def __init__(self, state: CacheState, data: ContentTierPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self.dev_name: str = data['devName']
        self.rank: int = data['rank']
        self.juice_value: int = data['juiceValue']
        self.juice_cost: int = data['juiceCost']
        self.highlight_color: str = data['highlightColor']
        self._display_icon: str = data['displayIcon']
        # self._old_display_icon: str = ''
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<ContentTier display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the content tier's name."""
        return self._display_name_localized

    @property
    def highlight_color_rgb(self) -> str:
        """:class: `str` Returns the content tier's highlight color RGB."""
        # rgba to rgb
        return self.highlight_color[:-1]

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the content tier's icon."""
        return Asset._from_url(self._state, self._display_icon)

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the content tier with the given UUID."""
    #     data = client._assets.get_content_tier(uuid)
    #     return cls(client=client, data=data) if data else None
