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
from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Union

from ..enums import CurrencyID, ItemType
from .bundle import FeaturedBundle
from .weapons import SkinNightMarket

if TYPE_CHECKING:
    from ..client import Client
    from ..types.store import (
        BonusStore as BonusStorePayload,
        BonusStoreOffer as BonusStoreOfferPayload,
        Bundle as BundlePayload,
        Entitlement as EntitlementPayload,
        EntitlementsByTypes as EntitlementsByTypesPayload,
        FeaturedBundle as FeaturedBundlePayload,
        Offer as OfferPayload,
        Offers as OffersPayload,
        Reward as RewardPayload,
        SkinsPanelLayout as SkinsPanelLayoutPayload,
        StoreFront as StoreFrontPayload,
        UpgradeCurrencyOffer as UpgradeCurrencyOfferPayload,
        Wallet as WalletPayload,
    )
    from .agent import Agent
    from .buddy import BuddyLevel
    from .contract import Contract
    from .player_card import PlayerCard
    from .player_title import PlayerTitle
    from .spray import Spray
    from .weapons import Skin, SkinChroma, SkinLevel

__all__ = (
    'Entitlements',
    'NightMarket',
    'Offer',
    'Offers',
    'StoreFront',
    'StoreOffer',
    'Wallet',
)


class StoreFront:

    __slot__ = ()

    def __init__(self, *, client: Any, data: StoreFrontPayload) -> None:
        self._client = client
        self._featured_bundle: FeaturedBundlePayload = data['FeaturedBundle']
        self._bundle: BundlePayload = self._featured_bundle['Bundle']
        self._bundles: List[BundlePayload] = self._featured_bundle.get('Bundles', [])
        self._skins_panel_layout: SkinsPanelLayoutPayload = data['SkinsPanelLayout']
        self._bonus_store: BonusStorePayload = data.get('BonusStore')

    def __repr__(self) -> str:
        attrs = [
            ('bundle', self.get_bundle()),
            ('bundles', self.get_bundles()),
            ('store', self.get_store()),
            ('nightmarket', self.get_nightmarket()),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def get_bundle(self) -> FeaturedBundle:
        """:class:`.models.Bundle`: The bundle in the featured panel."""
        return FeaturedBundle._from_store(client=self._client, bundle=self._bundle)

    def get_bundles(self) -> Union[List[FeaturedBundle]]:
        """:class:`.models.Bundle`: The list of bundles in the featured panel."""
        return [FeaturedBundle._from_store(client=self._client, bundle=bundle) for bundle in self._bundles]

    def get_store(self) -> StoreOffer:
        """:class:`.models.StoreOffer`: The store offer in the featured panel."""
        return StoreOffer(client=self._client, data=self._skins_panel_layout)

    def get_nightmarket(self) -> Optional[NightMarket]:
        """:class:`.models.NightMarketOffer`: The nightmarket offer in the featured panel."""
        return NightMarket(client=self._client, data=self._bonus_store) if self._bonus_store is not None else None


class StoreOffer:

    __slot__ = ()

    def __init__(self, *, client: Any, data: SkinsPanelLayoutPayload) -> None:
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
        return [self._client.get_skin(uuid=uuid) for uuid in self._skin_offers]

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

    def __init__(self, *, client: Client, data: BonusStorePayload) -> None:
        self._client = client
        self._skin_offers: List[BonusStoreOfferPayload] = data['BonusStoreOffers']
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
    def __init__(self, *, client: Client, data: WalletPayload) -> None:
        self._client = client
        self.balances = data['Balances']

    def __repr__(self) -> str:
        return f'<Wallet valorant_points={self.valorant_points!r} radiant_points={self.radiant_points!r}>'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Wallet)
            and self.valorant_points == other.valorant_points
            and self.radiant_points == other.radiant_points
        )

    @property
    def valorant_points(self) -> int:
        """Returns the valorant points for the wallet"""
        return self.balances.get('85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741', 0)

    @property
    def radiant_points(self) -> int:
        """Returns the radiant points for the wallet"""
        return self.balances.get('e59aa87c-4cbf-517a-5983-6e81511be9b7', 0)


class Reward:
    def __init__(self, data: RewardPayload) -> None:
        self.item_type_id: str = data['ItemTypeID']
        self.item_id: str = data['ItemID']
        self.quantity: int = data['Quantity']

    def __repr__(self) -> str:
        return f'<Reward item_type_id={self.item_type_id!r} item_id={self.item_id!r} quantity={self.quantity!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Reward) and self.item_id == other.item_id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Offer:
    def __init__(self, data: OfferPayload) -> None:
        self.id: str = data['OfferID']
        self._is_direct_purchase: bool = data['IsDirectPurchase']
        self.cost: int = data['Cost'][str(CurrencyID.valorant_point)]
        self.rewards: List[Reward] = [Reward(reward) for reward in data['Rewards']]

    def __repr__(self) -> str:
        return f'<Offer offer_id={self.id!r}>'

    def __int__(self) -> int:
        return self.cost

    def __bool__(self) -> bool:
        return self.is_direct_purchase()

    def is_direct_purchase(self) -> bool:
        """Returns if the offer is a direct purchase"""
        return self._is_direct_purchase

    # def item(self) -> Any:
    #     return self._client.get_
    # TODO: somethings wrong here


class UpgradeCurrencyOffer:
    def __init__(self, data: UpgradeCurrencyOfferPayload) -> None:
        self.offer_id: str = data['OfferID']
        self.store_front_item_id: str = data['StorefrontItemID']

    def __repr__(self) -> str:
        return f'<UpgradeCurrencyOffer offer_id={self.offer_id!r}>'


class Offers:
    def __init__(self, data: OffersPayload) -> None:
        self.offers: List[Offer] = [Offer(offer) for offer in data['Offers']]
        self.upgrade_currency_offer: List[UpgradeCurrencyOffer] = [
            UpgradeCurrencyOffer(offer) for offer in data['UpgradeCurrencyOffers']
        ]
        self.raw: OffersPayload = data

    def __repr__(self) -> str:
        return f'<Offers offers={self.offers!r}>'


class Entitlements:
    def __init__(self, client: Client, data: EntitlementsByTypesPayload) -> None:
        self._client = client
        self._data = data.get('EntitlementsByTypes', [])

    def __repr__(self) -> str:
        return f'<Entitlements>'

    def get_by_type(self, item_type: ItemType) -> List[EntitlementPayload]:
        """Returns the entitlements by type"""
        for entitlement in self._data:
            if entitlement['ItemTypeID'].lower() == str(item_type).lower():
                return entitlement['Entitlements']
        return []

    def get_agents(self) -> List[Agent]:
        """:class:`.models.Agent`: Returns a list of agents."""
        items = self.get_by_type(ItemType.agent)
        return [self._client.get_agent(uuid=item.get('ItemID')) for item in items]

    def get_skin_levels(self, level_one: bool = True) -> List[SkinLevel]:
        """:class:`.models.SkinLevel`: Returns a list of skin levels."""
        items = self.get_by_type(ItemType.skin_level)
        skins = []
        for item in items:
            skin = self._client.get_skin_level(uuid=item.get('ItemID'))
            if level_one:
                if skin.is_level_one():
                    skins.append(skin)
            else:
                skins.append(skin)
        return skins

    def get_skin_chromas(self) -> List[SkinChroma]:
        """:class:`.models.SkinChroma`: Returns a list of skin chromas."""
        items = self.get_by_type(ItemType.skin_chroma)
        return [self._client.get_skin_chroma(uuid=item.get('ItemID')) for item in items]

    def get_buddy_levels(self) -> List[BuddyLevel]:
        """:class:`.models.BuddyLevel`: Returns a list of buddy levels."""
        items = self.get_by_type(ItemType.buddy_level)
        # instance_id = item.get('InstanceID')  # What is this?
        # TODO: amount buddy levels owned
        return [self._client.get_buddy_level(uuid=item.get('ItemID')) for item in items]

    def get_sprays(self) -> List[Spray]:
        """:class:`.models.Spray`: Returns a list of sprays."""
        items = self.get_by_type(ItemType.spray)
        return [self._client.get_spray(uuid=item.get('ItemID')) for item in items]

    def get_player_cards(self) -> List[PlayerCard]:
        """:class:`.models.PlayerCard`: Returns a list of player cards."""
        items = self.get_by_type(ItemType.player_card)
        return [self._client.get_player_card(uuid=item.get('ItemID')) for item in items]

    def get_player_titles(self) -> List[PlayerTitle]:
        """:class:`.models.PlayerTitle`: Returns a list of player titles."""
        items = self.get_by_type(ItemType.player_title)
        return [self._client.get_player_title(uuid=item.get('ItemID')) for item in items]

    def get_contracts(self) -> List[Contract]:
        """:class:`.models.Contract`: Returns a list of contracts."""
        items = self.get_by_type(ItemType.contract)
        return [self._client.get_contract(uuid=item.get('ItemID')) for item in items]
