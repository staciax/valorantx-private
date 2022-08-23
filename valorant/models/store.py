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

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Iterator

from .bundle import Bundle
from .weapons import Skin, SkinNightMarket

if TYPE_CHECKING:
    from ..client import Client

__all__ = (
    'StoreFront',
    'StoreOffer',
    'NightMarket',
    'Wallet',
)


class StoreFront:

    __slot__ = ()

    def __init__(self, *, client: Any, data: Any) -> None:
        self._client = client
        self._featured_bundle: Dict[Any, Any] = data['FeaturedBundle']
        self._bundle: Dict[Any, Any] = self._featured_bundle['Bundle']
        self._bundles: Dict[Any, Any] = self._featured_bundle.get('Bundles', [])
        self._skins_panel_layout: Dict[Any, Any] = data['SkinsPanelLayout']
        self._bonus_store: Dict[Any, Any] = data.get('BonusStore')

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'<StoreFront bundles={self.bundles} store={self.store} nightmarket={self.nightmarket}>'

    @property
    def bundle(self) -> Bundle:
        """:class:`.models.Bundle`: The bundle in the featured panel."""
        return Bundle._from_store(client=self._client, bundle=self._bundle)

    @property
    def bundles(self) -> Union[List[Bundle]]:
        """:class:`.models.Bundle`: The list of bundles in the featured panel."""
        return [Bundle._from_store(client=self._client, bundle=bundle) for bundle in self._bundles]

    @property
    def store(self) -> StoreOffer:
        """:class:`.models.StoreOffer`: The store offer in the featured panel."""
        return StoreOffer(client=self._client, data=self._skins_panel_layout)

    @property
    def nightmarket(self) -> Optional[NightMarket]:
        """:class:`.models.NightMarketOffer`: The nightmarket offer in the featured panel."""
        return NightMarket(client=self._client, data=self._bonus_store) if self._bonus_store is not None else None


class StoreOffer:

    __slot__ = ()

    def __init__(self, *, client: Any, data: Any) -> None:
        self._client: Client = client
        self._skin_offers: List[str] = data['SingleItemOffers']
        self._duration: int = data['SingleItemOffersRemainingDurationInSeconds']

    def __repr__(self) -> str:
        return f'<StoreOffer skins={self.skins!r} duration={self.duration} reset_at={self.reset_at}>'

    def __len__(self) -> int:
        return len(self.skins)

    def __iter__(self) -> Iterator[Skin]:
        return iter(self.skins)

    @property
    def skins(self) -> List[Skin]:
        """:class:`.models.Skin`: The list of skins in the store offer."""
        return [Skin._from_uuid(client=self._client, uuid=uuid, all_type=True) for uuid in self._skin_offers]

    @property
    def duration(self) -> float:
        """:class:`float`: The duration of the store offer in seconds."""
        return self._duration

    @property
    def reset_at(self) -> datetime:
        """:class:`datetime.datetime`: The time when the store offer will reset."""
        dt = datetime.utcnow() + timedelta(seconds=self._duration)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt


class NightMarket:

    __slot__ = ()

    def __init__(self, *, client: Client, data: Any) -> None:
        self._client = client
        self._skin_offers: List[Dict[str, Any]] = data['BonusStoreOffers']
        self.duration: int = data['BonusStoreRemainingDurationInSeconds']

    def __repr__(self) -> str:
        return f'<NightMarket skins={self.skins!r} duration={self.duration}>'

    def __len__(self) -> int:
        return len(self.skins)

    def __iter__(self) -> Iterator[SkinNightMarket]:
        return iter(self.skins)

    @property
    def skins(self) -> List[SkinNightMarket]:
        """Returns a list of skins in the offer"""
        return [SkinNightMarket._from_data(client=self._client, skin_data=skin) for skin in self._skin_offers]

    @property
    def expire_at(self) -> datetime:
        """:class:`datetime.datetime`: The time when the offer will expire."""
        dt = datetime.utcnow() + timedelta(seconds=self.duration)
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
        """Returns the valorant points for the wallet"""
        return self.balances.get('85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741', 0)

    @property
    def radiant_points(self) -> int:
        """Returns the radiant points for the wallet"""
        return self.balances.get('e59aa87c-4cbf-517a-5983-6e81511be9b7', 0)
