from __future__ import annotations

from ..localization import Localization
from ..asset_manager import Asset

from .base import BaseObject
from typing import Any, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..client import Client

__all__ = (
    'Buddy',
    'Spray',
    'PlayerCard',
    'PlayerTitle'
)

# TODO: เอาออกบาง property เป็น variable และใส่ docs ของ class เข้าไป

class Buddy(BaseObject):

    def __init__(self, client: Client, data: Optional[Any], bundle: Any = None) -> None:
        super().__init__(client=client, data=data, bundle=bundle)

    def _update(self, data: Optional[Any]) -> None:
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._theme_uuid: Optional[str] = data.get('themeUuid')
        self._display_icon: Optional[str] = data.get('displayIcon')
        self._charm_level: int = data['charmLevel']
        self._asset_path: str = data['assetPath']
        self._price: int = data.get('price', 0)
        if self._extras.get('bundle') is not None:
            self._bundle: Any = self._extras['bundle']
            self._price: int = self._bundle.get('BasePrice', self._price)
            self._discounted_price: int = self._bundle.get('DiscountedPrice', self._price)
            self._is_promo: bool = self._bundle.get('IsPromoItem')
            self._currency_id: str = self._bundle.get('CurrencyID')
            self._discount_percent: float = self._bundle.get('DiscountPercent')

    def __repr__(self) -> str:
        return f'<Buddy uuid={self.uuid!r} name={self.name!r} price={self.price!r}>'

    def __str__(self) -> str:
        return self.name

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the buddy's name."""
        return self.name_localizations.american_english

    @property
    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the buddy is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @property
    def theme(self) -> str:  # TODO: Theme Object
        """ :class: `str` Returns the buddy's theme."""
        return self._theme_uuid

    @property
    def charm_level(self) -> int:
        """:class: `int` Returns the buddy's charm level."""
        return self._charm_level

    @property
    def icon(self) -> Asset:
        """:class: `Asset` Returns the buddy's icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the buddy's asset path."""
        return self._asset_path

    @property
    def price(self) -> int:
        """:class: `int` Returns the buddy's price."""
        return self._price

    # bundle

    @property
    def discounted_price(self) -> int:
        """ :class: `int` Returns the discounted price."""
        return self._discounted_price

    @property
    def discount_percent(self) -> float:
        """ :class: `float` Returns the discount percent."""
        return self._discount_percent

    @property
    def is_promo(self) -> bool:
        """ :class: `bool` Returns whether the bundle is a promo."""
        return self._is_promo

class Spray(BaseObject):

    def __init__(self, *, client: Client, data: Any, bundle: Any = None) -> None:
        super().__init__(client=client, data=data, bundle=bundle)

    def _update(self, data: Any) -> None:
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self._full_icon: Optional[str] = data['fullIcon']
        self._full_transparent_icon: Optional[str] = data['fullTransparentIcon']
        self._animation_png: Optional[str] = data['animationPng']
        self._animation_gif: Optional[str] = data['animationGif']
        self._spray_level: int = data['sprayLevel']
        self._asset_path: str = data['assetPath']
        self._price = data.get('price', 0)
        if self._extras.get('bundle') is not None:
            self._bundle: Any = self._extras['bundle']
            self._price: int = self._bundle.get('BasePrice', self._price)
            self._discounted_price: int = self._bundle.get('DiscountedPrice', self._price)
            self._is_promo: bool = self._bundle.get('IsPromoItem')
            self._currency_id: str = self._bundle.get('CurrencyID')
            self._discount_percent: float = self._bundle.get('DiscountPercent')

    def __repr__(self) -> str:
        return f"<Spray uuid={self.name!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    @property
    def uuid(self) -> str:
        """:class: `str` Returns the spray's uuid."""
        return self._uuid

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the skin's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the skin's name."""
        return self.name_localizations.american_english

    @property
    def icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the skin's icon."""
        if self._full_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._full_icon)

    @property
    def full_icon(self) -> Optional[Asset]:
        """ :class: `Asset` Returns the skin's full icon."""
        if self._full_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._full_icon)

    @property
    def full_transparent_icon(self) -> Optional[Asset]:
        """ :class: `Asset` Returns the skin's full transparent icon."""
        if self._full_transparent_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._full_transparent_icon)

    @property
    def animation_png(self) -> Optional[Asset]:
        """ :class: `Asset` Returns the skin's animation png."""
        if self._animation_png is None:
            return None
        return Asset._from_url(client=self._client, url=self._animation_png)

    @property
    def animation_gif(self) -> Optional[Asset]:
        """ :class: `Asset` Returns the skin's animation gif."""
        if self._animation_gif is None:
            return None
        return Asset._from_url(client=self._client, url=self._animation_gif)

    @property
    def spray_level(self) -> int:
        """:class: `int` Returns the skin's spray level."""
        return self._spray_level

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the skin's asset path."""
        return self._asset_path

    @property
    def price(self) -> int:
        """ :class: `int` Returns the skin's price."""
        return self._price

    # bundle

    @property
    def discounted_price(self) -> int:
        """ :class: `int` Returns the discounted price."""
        return self._discounted_price

    @property
    def discount_percent(self) -> float:
        """ :class: `float` Returns the discount percent."""
        return self._discount_percent

    @property
    def is_promo(self) -> bool:
        """ :class: `bool` Returns whether the bundle is a promo."""
        return self._is_promo

class PlayerCard(BaseObject):

    def __init__(self, *, client: Client, data: Any, bundle: Any = None) -> None:
        super().__init__(client=client, data=data, bundle=bundle)

    def _update(self, data: Any) -> None:
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._display_icon: Optional[str] = data['displayIcon']
        self._small_icon: Optional[str] = data['smallArt']
        self._wide_icon: Optional[str] = data['wideArt']
        self._large_icon: Optional[str] = data['largeArt']
        self._theme_uuid: Optional[str] = data['themeUuid']
        self._asset_path: str = data['assetPath']
        self._price = data.get('price', 0)
        if self._extras.get('bundle') is not None:
            self._bundle: Any = self._extras['bundle']
            self._price: int = self._bundle.get('BasePrice', self._price)
            self._discounted_price: int = self._bundle.get('DiscountedPrice', self._price)
            self._is_promo: bool = self._bundle.get('IsPromoItem')
            self._currency_id: str = self._bundle.get('CurrencyID')
            self._discount_percent: float = self._bundle.get('DiscountPercent')

    def __repr__(self) -> str:
        return f"<PlayerCard uuid={self.name!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    @property
    def uuid(self) -> str:
        """:class: `str` Returns the player card's uuid."""
        return self._uuid

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the buddy's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the buddy's name."""
        return self.name_localizations.american_english

    @property
    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the player card is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @property
    def icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the buddy's icon."""
        if self._display_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def small_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the buddy's small icon."""
        if self._small_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._small_icon)

    @property
    def wide_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the buddy's wide icon."""
        if self._wide_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._wide_icon)

    @property
    def large_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the buddy's large icon."""
        if self._large_icon is None:
            return None
        return Asset._from_url(client=self._client, url=self._large_icon)

    @property
    def theme_uuid(self) -> Optional[str]:
        """:class: `str` Returns the buddy's theme uuid."""
        return self._theme_uuid

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the buddy's asset path."""
        return self._asset_path

    @property
    def price(self) -> int:
        """ :class: `int` Returns the buddy's price."""
        return self._price

    @property
    def discounted_price(self) -> int:
        """ :class: `int` Returns the discounted price."""
        return self._discounted_price

    @property
    def discount_percent(self) -> float:
        """ :class: `float` Returns the discount percent."""
        return self._discount_percent

    @property
    def is_promo(self) -> bool:
        """ :class: `bool` Returns whether the buddy is a promo."""
        return self._is_promo

    @property
    def currency_id(self) -> str:
        """:class: `str` Returns the currency id."""
        return self._currency_id

    # @property
    # def is_owned(self) -> bool:
    #     """:class: `bool` Returns whether the player card is owned."""
    #     return self._client.player_cards.is_owned(self.uuid)

class PlayerTitle(BaseObject):

    def __init__(self, *, client: Client, data: Any,) -> None:
        super().__init__(client=client, data=data)

    def __repr__(self) -> str:
        return f"<PlayerTitle uuid={self.name!r} name={self.name!r}>"

    def __str__(self) -> str:
        return self.name

    def _update(self, data: Any) -> None:
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._title_text: Union[str, Dict[str, str]] = data['titleText']
        self._is_hidden_if_not_owned: bool = data['isHiddenIfNotOwned']
        self._asset_path: str = data['assetPath']

    @property
    def uuid(self) -> str:
        """:class: `str` Returns the player title's uuid."""
        return self._uuid

    @property
    def name_localizations(self) -> Localization:
        """:class: `Translator` Returns the player title's names."""

        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the player title's name."""
        return self.name_localizations.american_english

    @property
    def title_text_localizations(self) -> Localization:
        """:class: `Translator` Returns the player title's title text."""

        return Localization(self._title_text, locale=self._client.locale)

    @property
    def title_text(self) -> str:
        """:class: `str` Returns the player title's title text."""
        return self.title_text_localizations.american_english

    @property
    def is_hidden_if_not_owned(self) -> bool:
        """:class: `bool` Returns whether the player title is hidden if not owned."""
        return self._is_hidden_if_not_owned

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the player title's asset path."""
        return self._asset_path
