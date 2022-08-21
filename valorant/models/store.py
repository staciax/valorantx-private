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

# from .skin import SkinNightMarket
from datetime import datetime, timezone, timedelta

from .weapons import Skin
from .bundle import Bundle


from typing import Any, Mapping, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

__all__ = (
    'StoreNightMarketOffer',
    'StoreFront',
    'StoreOffer',
    'Wallet',
)

class StoreFront:

    def __init__(self, *, client: Any, data: Any) -> None:
        self._client = client
        self.data = data

    @property
    def bundle(self) -> Bundle:
        """ Returns the bundle for the storefront """
        return Bundle._from_store(client=self._client, bundle=self.data['FeaturedBundle']['Bundle'])

    @property
    def bundles(self) -> List[Bundle]:
        """ Returns a list of bundles """
        return [
            Bundle._from_store(client=self._client, bundle=bundle)
            for bundle in self.data['FeaturedBundle']['Bundles']
        ]

    @property
    def store(self) -> StoreOffer:
        return StoreOffer(client=self._client, data=self.data['SkinsPanelLayout'])

    @property
    def nightmarket(self) -> Optional[StoreNightMarketOffer]:
        """ alias for offers """
        if 'BonusStore' in self.data:
            return StoreNightMarketOffer(client=self._client, data=self.data['BonusStore'])
        return None

    # alias
    @property
    def shop(self) -> StoreOffer:
        """ alias for store """
        return self.store

class StoreOffer:

    __slot__ = ('_client', '_skin_offers', '_duration')

    def __init__(self, *, client: Any, data: Any) -> None:
        self._client: Client = client
        self._skin_offers: List[str] = data['SingleItemOffers']
        self._duration: int = data['SingleItemOffersRemainingDurationInSeconds']

    @property
    def skins(self) -> List[Skin]:
        """ Returns a list of skins in the offer """
        return [Skin._from_uuid(client=self._client, uuid=uuid) for uuid in self._skin_offers]

    @property
    def duration(self) -> float:
        """ Returns the duration of the offer in seconds """
        return self._duration

    @property
    def resets_at(self) -> datetime:
        dt = datetime.utcnow() + timedelta(seconds=self._duration)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

class StoreNightMarketOffer:
    duration: int
    _skin_offers: List[str]

    __slot__ = ('data', '_skin_offers', 'duration')

    def __init__(self, *, client: Client, data: Any) -> None:
        self._client = client
        self.data = data
        self._skin_offers: Mapping = data['BonusStoreOffers']
        self._duration = data['BonusStoreRemainingDurationInSeconds']

    @property
    def skins(self) -> List[Skin]:
        """ Returns a list of skins in the offer """
        return [Skin._from_uuid(client=self._client, extras=skin) for skin in self._skin_offers]

    @property
    def duration(self) -> float:
        """ Returns the duration of the offer in seconds """
        return self._duration

    @property
    def expires_at(self) -> datetime:
        dt = datetime.utcnow() + timedelta(seconds=self._duration)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

class Wallet:

    def __init__(self, *, client: Client, data: Any) -> None:
        self._client = client
        self._update(data)

    def __repr__(self) -> str:
        return f'<Wallet valorant_points={self.valorant_points!r} radiant_points={self.radiant_points!r}>'

    def _update(self, data: Any) -> None:
        self.balances = data['Balances']

    @property
    def valorant_points(self) -> int:
        """ Returns the valorant points for the wallet """
        return self.balances.get('85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741', 0)

    @property
    def radiant_points(self) -> int:
        """ Returns the radiant points for the wallet """
        return self.balances.get('e59aa87c-4cbf-517a-5983-6e81511be9b7', 0)