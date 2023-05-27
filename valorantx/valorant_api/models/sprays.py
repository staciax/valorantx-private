from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Generic, List, Optional, TypeVar, Union

from .. import utils
from ..asset import Asset
from ..enums import ItemType, Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..cache import CacheState
    from ..types.sprays import Spray as SprayPayload, SprayLevel as SprayLevelPayload
    from .themes import Theme

__all__ = (
    'Spray',
    'SprayLevel',
)

SprayT = TypeVar('SprayT', bound='Spray')


class Spray(BaseModel):
    def __init__(self, *, state: CacheState, data: SprayPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._data: SprayPayload = data
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._category: Optional[str] = data['category']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self._display_icon: str = data['displayIcon']
        self._full_icon: Optional[str] = data['fullIcon']
        self._full_transparent_icon: Optional[str] = data['fullTransparentIcon']
        self._animation_png: Optional[str] = data['animationPng']
        self._animation_gif: Optional[str] = data['animationGif']
        self.asset_path: str = data['assetPath']
        self.levels: List[SprayLevel] = [SprayLevel(state=self._state, data=level, parent=self) for level in data['levels']]
        self.type: ItemType = ItemType.spray
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f"<Spray display_name={self.display_name!r}>"

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the skin's name."""
        return self._display_name_localized

    @property
    def category(self) -> Optional[str]:
        """:class: `str` Returns the skin's category."""
        if self._category is None:
            return None
        return utils.removeprefix(self._category, 'EAresSprayCategory::')

    @property
    def theme(self) -> Optional[Theme]:
        if self._theme_uuid is None:
            return None
        return self._state.get_theme(self._theme_uuid)

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        return Asset._from_url(state=self._state, url=self._display_icon)

    @property
    def full_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's full icon."""
        if self._full_icon is None:
            return None
        return Asset._from_url(state=self._state, url=self._full_icon)

    @property
    def full_transparent_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's full transparent icon."""
        if self._full_transparent_icon is None:
            return None
        return Asset._from_url(state=self._state, url=self._full_transparent_icon)

    @property
    def animation_png(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's animation png."""
        if self._animation_png is None:
            return None
        return Asset._from_url(state=self._state, url=self._animation_png)

    @property
    def animation_gif(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's animation gif."""
        if self._animation_gif is None:
            return None
        return Asset._from_url(state=self._state, url=self._animation_gif)

    @classmethod
    def _copy(cls, spray: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = spray._uuid
        self._state = spray._state
        self._data = spray._data.copy()
        self._display_name = spray._display_name
        self._category = spray._category
        self._theme_uuid = spray._theme_uuid
        self._display_icon = spray._display_icon
        self._full_icon = spray._full_icon
        self._full_transparent_icon = spray._full_transparent_icon
        self._animation_png = spray._animation_png
        self._animation_gif = spray._animation_gif
        self.asset_path = spray.asset_path
        self.levels = spray.levels.copy()
        self.type = spray.type
        self._display_name_localized = spray._display_name_localized
        return self

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the spray with the given uuid."""
    #     data = client._assets.get_spray(uuid=uuid)
    #     return cls(client=client, data=data) if data else None


class SprayLevel(BaseModel, Generic[SprayT]):
    def __init__(self, state: CacheState, data: SprayLevelPayload, parent: SprayT) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._data: SprayLevelPayload = data
        self.spray_level: int = data['sprayLevel']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']
        self.type: ItemType = ItemType.spray_level
        self.parent: SprayT = parent
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<SprayLevel display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the spray's name."""
        return self._display_name_localized

    @property
    def level(self) -> int:
        """:class: `int` alias for :attr: `SprayLevel.spray_level`"""
        return self.spray_level

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `str` Returns the spray's display icon."""
        return Asset._from_url(state=self._state, url=self._display_icon) if self._display_icon else None

    @classmethod
    def _copy(cls, spray_level: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self._uuid = spray_level._uuid
        self._state = spray_level._state
        self._data = spray_level._data.copy()
        self.spray_level = spray_level.spray_level
        self._display_name = spray_level._display_name
        self._display_icon = spray_level._display_icon
        self.asset_path = spray_level.asset_path
        self.type = spray_level.type
        self.parent = spray_level.parent._copy(spray_level.parent)
        self._display_name_localized = spray_level._display_name_localized
        return self

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the spray level with the given uuid."""
    #     data = client._assets.get_spray_level(uuid=uuid)
    #     return cls(client=client, data=data) if data else None
