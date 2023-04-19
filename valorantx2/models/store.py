from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from ..enums import RADIANITE_POINT_UUID, VALORANT_POINT_UUID
from ..valorant_api_cache import CacheState
from .bundles import FeaturedBundle
from .weapons import SkinLevelOffer

if TYPE_CHECKING:
    from ..types.store import (
        BonusStore as BonusStorePayload,
        Entitlements as EntitlementsPayload,
        Offer as OfferPayload,
        Offers as OffersPayload,
        Reward as RewardPayload,
        SkinsPanelLayout as SkinsPanelLayoutPayload,
        StoreFront as StoreFrontPayload,
        Wallet as WalletPayload,
    )
    from .weapons import SkinLevel

__all__ = (
    'StoreFront',
    'Wallet',
    'Entitlements',
    'Offers',
)


class SkinsPanelLayout:
    def __init__(self, state: CacheState, data: SkinsPanelLayoutPayload):
        self._state = state
        self.skins: List[SkinLevelOffer] = []
        for skin_offer in data['SingleItemStoreOffers']:
            skin = SkinLevelOffer.from_data(state=state, data_offer=skin_offer)
            if skin is not None:
                self.skins.append(skin)
        self._remaining_duration_in_seconds: int = data['SingleItemOffersRemainingDurationInSeconds']

    @property
    def remaining_time(self) -> datetime.datetime:
        dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._remaining_duration_in_seconds)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt


class BonusStore:
    def __init__(self, state: CacheState, data: BonusStorePayload):
        self._state = state
        self.skins: List[SkinLevel] = [self._state.get_skin_level(offer['Offer']['OfferID']) for offer in data['BonusStoreOffers']]  # type: ignore
        self._bonus_store_remaining_duration_in_seconds: int = data['BonusStoreRemainingDurationInSeconds']

    @property
    def remaining_duration(self) -> datetime.datetime:
        dt = datetime.datetime.now() + datetime.timedelta(seconds=self._bonus_store_remaining_duration_in_seconds)
        return dt


class StoreFront:
    def __init__(self, state: CacheState, data: StoreFrontPayload):
        self._state = state
        self.skins_panel_layout: SkinsPanelLayout = SkinsPanelLayout(state, data['SkinsPanelLayout'])
        self.bundle: Optional[FeaturedBundle] = FeaturedBundle.from_data(state, data['FeaturedBundle']['Bundle'])
        self.bundles: List[Optional[FeaturedBundle]] = [
            FeaturedBundle.from_data(state, bundle) for bundle in data['FeaturedBundle']['Bundles']
        ]
        self.bonus_store: Optional[BonusStore] = None
        if 'BonusStore' in data:
            self.bonus_store = BonusStore(state, data['BonusStore'])

    @property
    def daily_store(self) -> SkinsPanelLayout:
        return self.skins_panel_layout

    @property
    def nightmarket(self) -> Optional[BonusStore]:
        return self.bonus_store


class Wallet:
    def __init__(self, state: CacheState, data: WalletPayload) -> None:
        self._state = state
        self._balances = data['Balances']
        self._valorant_value: int = self._balances.get(VALORANT_POINT_UUID, 0)
        self._radiant_value: int = self._balances.get(RADIANITE_POINT_UUID, 0)
        # self._valorant_points: Optional[ValorantAPICurrency] = self._client.valorant_api.get_currency(uuid='85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741')
        # self._radiant_points: Optional[ValorantAPICurrency] = self._client.valorant_api.get_currency(uuid='e59aa87c-4cbf-517a-5983-6e81511be9b7')
        # if self._valorant_points is not None:
        #     self._valorant_points.value = self._valorant_value
        # if self._radiant_points is not None:
        #     self._radiant_points.value = self._radiant_value

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
        return self._valorant_value

    @property
    def radiant_points(self) -> int:
        """Returns the radiant points for the wallet"""
        return self._radiant_value

    # def get_valorant(self) -> Optional[Currency]:
    #     return self._valorant_points

    # def get_radiant(self) -> Optional[Currency]:
    #     return self._radiant_points


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

    # @property
    # def item(self) -> Any:
    #     ...


class Offer:
    def __init__(self, data: OfferPayload, item: Optional[Any] = None) -> None:
        self.id: str = data['OfferID']
        self._is_direct_purchase: bool = data['IsDirectPurchase']
        self.cost: int = data['Cost'][VALORANT_POINT_UUID]
        self.rewards: List[Reward] = [Reward(reward) for reward in data['Rewards']]
        self.item: Optional[Any] = item

    def __repr__(self) -> str:
        return f'<Offer offer_id={self.id!r}>'

    def __int__(self) -> int:
        return self.cost

    def __bool__(self) -> bool:
        return self.is_direct_purchase()

    def is_direct_purchase(self) -> bool:
        """Returns if the offer is a direct purchase"""
        return self._is_direct_purchase


class Offers:
    def __init__(self, data: OffersPayload) -> None:
        self.offers: List[Offer] = [Offer(offer) for offer in data['Offers']]

    def __repr__(self) -> str:
        return f'<Offers offers={self.offers!r}>'


class Entitlements:
    def __init__(self, state: CacheState, data: EntitlementsPayload) -> None:
        self._state = state
        # self._data = data.get('EntitlementsByTypes', [])
        # self._agents: List[Agent] = []
        # self._skin_levels: List[Skin] = []
        # self._skin_chromas: List[Skin] = []
        # self._buddy_levels: List[Buddy] = []
        # self._sprays: List[Buddy] = []
        # self._player_cards: List[PlayerCard] = []
        # self._player_titles: List[PlayerTitle] = []
        # self._contracts: List[Contract] = []

    # def __repr__(self) -> str:
    #     return f'<Entitlements> agents={len(self.agents)} skin_levels={len(self.skin_levels)} skin_chromas={len(self.skin_chromas)} buddy_levels={len(self.buddy_levels)} sprays={len(self.sprays)} player_cards={len(self.player_cards)} player_titles={len(self.player_titles)} contracts={len(self.contracts)}>'

    # def get_by_type(self, item_type: ItemType) -> List[EntitlementPayload]:
    #     """Returns the entitlements by type"""
    #     for entitlement in self._data:
    #         if entitlement['ItemTypeID'].lower() == str(item_type).lower():
    #             return entitlement['Entitlements']
    #     return []

    # @property
    # def agents(self) -> List[Agent]:
    #     """:class:`.models.Agent`: Returns a list of agents."""
    #     items = self.get_by_type(ItemType.agent)
    #     agents = []
    #     for item in items:
    #         agent = self._client.get_agent(uuid=item.get('ItemID'))
    #         if agent is not None:
    #             agents.append(agent)
    #     return agents

    # @property
    # def skin_levels(self, level_one: bool = True) -> List[SkinLevel]:
    #     """:class:`.models.SkinLevel`: Returns a list of skin levels."""
    #     items = self.get_by_type(ItemType.skin_level)
    #     skins = []
    #     for item in items:
    #         skin = self._client.get_skin_level(uuid=item.get('ItemID'))
    #         if level_one:
    #             if skin is not None:
    #                 if skin.is_level_one():
    #                     skins.append(skin)
    #         else:
    #             skins.append(skin)
    #     return skins

    # @property
    # def skin_chromas(self) -> List[SkinChroma]:
    #     """:class:`.models.SkinChroma`: Returns a list of skin chromas."""
    #     items = self.get_by_type(ItemType.skin_chroma)
    #     chromas = []
    #     for item in items:
    #         chroma = self._client.get_skin_chroma(uuid=item.get('ItemID'))
    #         if chroma is not None:
    #             chromas.append(chroma)

    #     return chromas

    # @property
    # def buddy_levels(self) -> List[BuddyLevel]:
    #     """:class:`.models.BuddyLevel`: Returns a list of buddy levels."""
    #     items = self.get_by_type(ItemType.buddy_level)
    #     # instance_id = item.get('InstanceID')  # What is this?
    #     # TODO: amount buddy levels owned
    #     buddy_levels = []
    #     for item in items:
    #         buddy = self._client.get_buddy_level(uuid=item.get('ItemID'))
    #         if buddy is not None:
    #             buddy_levels.append(buddy)
    #     return buddy_levels

    # @property
    # def sprays(self) -> List[Spray]:
    #     """:class:`.models.Spray`: Returns a list of sprays."""
    #     items = self.get_by_type(ItemType.spray)
    #     sprays = []
    #     for item in items:
    #         spray = self._client.get_spray(uuid=item.get('ItemID'))
    #         if spray is not None:
    #             sprays.append(spray)
    #     return sprays

    # @property
    # def player_cards(self) -> List[PlayerCard]:
    #     """:class:`.models.PlayerCard`: Returns a list of player cards."""
    #     items = self.get_by_type(ItemType.player_card)
    #     player_cards = []
    #     for item in items:
    #         player_card = self._client.get_player_card(uuid=item.get('ItemID'))
    #         if player_card is not None:
    #             player_cards.append(player_card)
    #     return player_cards

    # @property
    # def player_titles(self) -> List[PlayerTitle]:
    #     """:class:`.models.PlayerTitle`: Returns a list of player titles."""
    #     items = self.get_by_type(ItemType.player_title)
    #     player_titles = []
    #     for item in items:
    #         player_title = self._client.get_player_title(uuid=item.get('ItemID'))
    #         if player_title is not None:
    #             player_titles.append(player_title)
    #     return player_titles

    # @property
    # def contracts(self) -> List[Contract]:
    #     """:class:`.models.Contract`: Returns a list of contracts."""
    #     items = self.get_by_type(ItemType.contract)
    #     contracts = []
    #     for item in items:
    #         contract = self._client.get_contract(uuid=item.get('ItemID'))
    #         if contract is not None:
    #             contracts.append(contract)
    #     return contracts
