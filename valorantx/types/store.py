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

from typing import TYPE_CHECKING, List, TypedDict, Union

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class Item(TypedDict):
    ItemTypeID: str
    ItemID: str
    Amount: int


class BundleItem(TypedDict):
    Item: Item
    BasePrice: int
    CurrencyID: str
    DiscountPercent: float
    DiscountedPrice: int
    IsPromoItem: bool


class BundleT(TypedDict):
    ID: str
    DataAssetID: str
    CurrencyID: str
    Items: List[BundleItem]
    DurationRemainingInSeconds: int
    WholesaleOnly: bool


class FeaturedBundle(TypedDict):
    Bundle: BundleT
    Bundles: List[BundleT]
    BundleRemainingDurationInSeconds: int


class SkinsPanelLayout(TypedDict):
    SingleItemOffers: List[str]
    SingleItemOffersRemainingDurationInSeconds: int


Cost = TypedDict(
    'Cost',
    {
        '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741': int,
    },
)

DiscountCosts = TypedDict(
    'DiscountCosts',
    {
        '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741': int,
    },
)


class Reward(TypedDict):
    ItemTypeID: str
    ItemID: str
    Quantity: int


class Offer(TypedDict):
    OfferID: str
    IsDirectPurchase: bool
    StartDate: str
    Cost: Union[str, Cost]
    Rewards: List[Reward]


class BonusStoreOffer(TypedDict):
    BonusOfferID: str
    Offer: str
    DiscountPercent: int
    DiscountCosts: DiscountCosts
    IsSeen: bool


class BonusStoreT(TypedDict):
    BonusStoreOffers: List[BonusStoreOffer]
    BonusStoreRemainingDurationInSeconds: int


class StoreFront(TypedDict, total=False):
    FeaturedBundle: FeaturedBundle
    SkinsPanelLayout: SkinsPanelLayout
    BonusStore: NotRequired[BonusStoreT]


Balances = TypedDict(
    'Balances',
    {
        '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741': int,
        'e59aa87c-4cbf-517a-5983-6e81511be9b7': int,
        'f08d4ae3-939c-4576-ab26-09ce1f23bb37': int,
    },
)


class Wallet(TypedDict):
    Balances: Balances


class UpgradeCurrencyOffer(TypedDict):
    OfferID: str
    StorefrontItemID: str


class Offers(TypedDict):
    Offers: List[Offer]
    UpgradeCurrencyOffers: List[UpgradeCurrencyOffer]


class Entitlement(TypedDict):
    TypeID: str
    ItemID: str
    InstanceID: NotRequired[str]


class Entitlements(TypedDict):
    ItemTypeID: str
    Entitlements: List[Entitlement]


class EntitlementsByTypes(TypedDict):
    EntitlementsByTypes: List[Entitlements]


class ItemFeaturedBundle(TypedDict):
    ItemTypeID: str
    ItemID: str
    Amount: int


class FeaturedBundleItem(TypedDict):
    Item: ItemFeaturedBundle
    BasePrice: int
    CurrencyID: str
    DiscountPercent: int
    DiscountedPrice: int
    IsPromoItem: bool
