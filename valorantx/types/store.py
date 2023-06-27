from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class Item(TypedDict):
    ItemTypeID: str
    ItemID: str
    Amount: int


class Reward(TypedDict):
    ItemTypeID: str
    ItemID: str
    Quantity: int


# Cost = TypedDict(
#     'Cost',
#     {
#         '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741': int,
#     },
# )

Cost = Dict[str, int]


class Offer(TypedDict):
    OfferID: str
    IsDirectPurchase: bool
    StartDate: str
    Cost: Cost
    Rewards: List[Reward]


class BundleItemOffer(TypedDict):
    BundleItemOfferID: str
    Offer: Offer
    DiscountPercent: int
    DiscountedCost: Cost


class Items(TypedDict):
    Item: Item
    BasePrice: int
    CurrencyID: str
    DiscountPercent: int
    DiscountedPrice: int
    IsPromoItem: bool


class Bundle_(TypedDict):
    ID: str
    DataAssetID: str
    CurrencyID: str
    Items: List[Items]
    ItemOffers: Optional[List[BundleItemOffer]]
    TotalBaseCost: Optional[Cost]
    TotalDiscountedCost: Optional[Cost]
    TotalDiscountPercent: float
    DurationRemainingInSeconds: int
    WholesaleOnly: bool


class FeaturedBundle(TypedDict):
    Bundle: Bundle_
    Bundles: List[Bundle_]
    BundleRemainingDurationInSeconds: int


class SkinsPanelLayout(TypedDict):
    SingleItemOffers: List[str]
    SingleItemStoreOffers: List[Offer]
    SingleItemOffersRemainingDurationInSeconds: int


class CurrencyOffer(TypedDict):
    OfferID: str
    StorefrontItemID: str
    Offer: Offer


class UpgradeCurrencyStore(TypedDict):
    UpgradeCurrencyOffers: List[CurrencyOffer]


class BonusStoreOffer(TypedDict):
    BonusOfferID: str
    Offer: Offer
    DiscountPercent: int
    DiscountCosts: Cost
    IsSeen: bool


class BonusStore(TypedDict):
    BonusStoreOffers: List[BonusStoreOffer]
    BonusStoreRemainingDurationInSeconds: int


class StoreFront(TypedDict):
    FeaturedBundle: FeaturedBundle
    SkinsPanelLayout: SkinsPanelLayout
    UpgradeCurrencyStore: UpgradeCurrencyStore
    BonusStore: NotRequired[BonusStore]
    AccessoryStore: AccessoryStore


class Wallet(TypedDict):
    Balances: Dict[str, int]


class Entitlement(TypedDict):
    TypeID: str
    ItemID: str


class EntitlementsByType(TypedDict):
    ItemTypeID: str
    Entitlements: List[Entitlement]


class Entitlements(TypedDict):
    EntitlementsByTypes: List[EntitlementsByType]


class Offers(TypedDict):
    Offers: List[Offer]


class AgentStoreFront(TypedDict):
    AgentStore: AgentStore


class AgentStore(TypedDict):
    AgentStoreOffers: List[AgentStoreOffer]
    FeaturedAgent: str


class AgentStoreOffer(TypedDict):
    AgentID: str
    StoreOffers: List[Offer]


class AccessoryStoreOffer(TypedDict):
    Offer: Offer
    ContractID: str


class AccessoryStore(TypedDict):
    AccessoryStoreOffers: List[AccessoryStoreOffer]
    AccessoryStoreRemainingDurationInSeconds: int
    StorefrontID: str
