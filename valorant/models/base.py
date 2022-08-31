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

from typing import TYPE_CHECKING, Any, Dict, Union

if TYPE_CHECKING:
    from ..client import Client


class _ModelTag:
    __slots__ = ()
    uuid: str


class BaseModel(_ModelTag):
    __slots__ = (
        '_uuid',
        '_client',
        '_extras',
    )

    if TYPE_CHECKING:
        uuid: str
        _client: Client

    def __init__(self, client: Client, data: Union[Any, Any], **kwargs: Any) -> None:
        self._client = client
        self._uuid: str = data.get('uuid')
        self._extras = kwargs
        self._update(data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} uuid={self.uuid!r}>"

    def __hash__(self) -> int:
        return hash(self.uuid)

    def _update(self, data: Union[Any, Any]) -> None:
        pass

    @property
    def uuid(self) -> str:
        """:class:`str`: The uuid of the object."""
        return self._uuid


class BaseFeaturedBundleItem:

    if TYPE_CHECKING:
        price: int

    def __init__(self, bundle: Dict[str, Any]) -> None:
        self.price: int = bundle.get('BasePrice', self.price)
        self.discounted_price: int = bundle.get('DiscountedPrice', self.price)
        self._is_promo: bool = bundle.get('IsPromoItem', False)
        self._currency_id: str = bundle.get('CurrencyID')
        self.discount_percent: float = bundle.get('DiscountPercent', 0.0)
        self.amount: int = bundle['Item']['Amount']

    def is_promo(self) -> bool:
        """:class: `bool` Returns whether the bundle is a promo."""
        return self._is_promo
