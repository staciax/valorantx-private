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

import abc
from typing import TYPE_CHECKING, Any, Mapping, Optional

from ..enums import MeleeWeaponID

if TYPE_CHECKING:
    from ..client import Client
    from ..types.store import FeaturedBundleItem as FeaturedBundleItemPayload
    from .currency import Currency

__all__ = (
    'BaseModel',
    'BaseFeaturedBundleItem',
)


class BaseModel(abc.ABC):

    __slots__ = (
        '_uuid',
        '_client',
        '_extras',
    )

    def __init__(self, client: Client, data: Optional[Mapping[str, Any]], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client: Client = client
        self._uuid: str = data.get('uuid') if data is not None else ''
        self._extras: Optional[Mapping[str, Any]] = kwargs

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} uuid={self.uuid!r}>"

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BaseModel) and other.uuid == self.uuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def uuid(self) -> str:
        """:class:`str`: The uuid of the object."""
        return self._uuid


class BaseFeaturedBundleItem:

    if TYPE_CHECKING:
        _client: Client

    def __init__(self, bundle: FeaturedBundleItemPayload) -> None:
        self.price: int = bundle.get('BasePrice')
        self.discounted_price: int = bundle.get('DiscountedPrice', 0)
        self._is_promo: bool = bundle.get('IsPromoItem', False)
        self._currency_id: str = bundle.get('CurrencyID')
        self.discount_percent: float = bundle.get('DiscountPercent', 0.0)
        self.amount: int = bundle['Item']['Amount']

    def is_promo(self) -> bool:
        """:class: `bool` Returns whether the bundle is a promo."""
        return self._is_promo

    def is_melee(self) -> bool:
        """:class: `bool` Returns whether the bundle is a melee weapon."""
        if hasattr(self, 'get_weapon'):
            if callable(self.get_weapon):
                weapon = self.get_weapon()
                return weapon.is_melee()
        return False

    @property
    def currency(self) -> Optional[Currency]:
        """:class:`Currency`: The currency of the bundles."""
        return self._client.get_currency(uuid=self._currency_id)