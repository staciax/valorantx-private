from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any, List, Optional, Union

from ..enums import KINGDOM_POINT_UUID, RADIANITE_POINT_UUID, VALORANT_POINT_UUID, ItemTypeID, try_enum
from ..valorant_api_cache import CacheState
from .bundles import FeaturedBundle
from .weapons import SkinLevelBonus, SkinLevelOffer

if TYPE_CHECKING:
    from ..client import Client
    from ..types.store import (
        AccessoryStore as AccessoryStorePayload,
        AccessoryStoreOffer as AccessoryStoreOfferPayload,
        AgentStore as AgentStorePayload,
        AgentStoreOffer as AgentStoreOfferPayload,
        BonusStore as BonusStorePayload,
        Entitlements as EntitlementsPayload,
        EntitlementsByType as EntitlementsByTypePayload,
        Offer as OfferPayload,
        Offers as OffersPayload,
        Reward as RewardPayload,
        SkinsPanelLayout as SkinsPanelLayoutPayload,
        StoreFront as StoreFrontPayload,
        Wallet as WalletPayload,
    )
    from .agents import Agent
    from .buddies import BuddyLevel
    from .contracts import ContractValorantAPI, RecruitmentProgressUpdate
    from .currencies import Currency
    from .player_cards import PlayerCard
    from .player_titles import PlayerTitle
    from .sprays import Spray, SprayLevel
    from .weapons import SkinChroma, SkinLevel

    RewardItem = Union[
        Agent,
        BuddyLevel,
        ContractValorantAPI,
        SkinLevel,
        SkinChroma,
        Spray,
        SprayLevel,
        PlayerCard,
        PlayerTitle,
        Currency,
    ]

__all__ = (
    'BonusStore',
    'Entitlements',
    'Offers',
    'SkinsPanelLayout',
    'StoreFront',
    'Wallet',
    'AccessoryStore',
    'AccessoryStoreOffer',
    'AgentStore',
    'AgentStoreOffer',
)

_log = logging.getLogger(__name__)


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
    def remaining_time_utc(self) -> datetime.datetime:
        dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._remaining_duration_in_seconds)
        return dt


class BonusStore:
    def __init__(self, state: CacheState, data: BonusStorePayload):
        self._state = state
        self.skins: List[SkinLevelBonus] = []
        for skin_offer in data['BonusStoreOffers']:
            skin = SkinLevelBonus.from_data(state=state, data_bonus=skin_offer)
            if skin is not None:
                self.skins.append(skin)
        self._bonus_store_remaining_duration_in_seconds: int = data['BonusStoreRemainingDurationInSeconds']

    @property
    def remaining_time_utc(self) -> datetime.datetime:
        dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._bonus_store_remaining_duration_in_seconds)
        return dt


class StoreFront:
    def __init__(self, state: CacheState, data: StoreFrontPayload):
        self._state = state
        self.skins_panel_layout: SkinsPanelLayout = SkinsPanelLayout(state, data['SkinsPanelLayout'])
        self.bundle: Optional[FeaturedBundle] = FeaturedBundle.from_data(state, data['FeaturedBundle']['Bundle'])
        self.bundles: List[FeaturedBundle] = []

        for bundle in data['FeaturedBundle']['Bundles']:
            bd = FeaturedBundle.from_data(state, bundle)
            if bd is not None:
                self.bundles.append(bd)

        if len(self.bundles) == 0 and self.bundle is not None:
            _log.warning(
                "No bundles found, but bundle is not None. Maybe the game is updating?. trying update client use 'client.??"
            )
            # TODO:: method to update client

        self.bonus_store: Optional[BonusStore] = None
        if 'BonusStore' in data:
            self.bonus_store = BonusStore(state, data['BonusStore'])

        self.accessory_store: AccessoryStore = AccessoryStore(state, data['AccessoryStore'])

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
        self._kingdom_value: int = self._balances.get(KINGDOM_POINT_UUID, 0)

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

    @property
    def kingdom_points(self) -> int:
        """Returns the kingdom points for the wallet"""
        return self._kingdom_value

    # helper methods

    def get_valorant_currency(self) -> Optional[Currency]:
        return self._state.get_currency(VALORANT_POINT_UUID)

    def get_radiant_currency(self) -> Optional[Currency]:
        return self._state.get_currency(RADIANITE_POINT_UUID)

    def get_kingdom_currency(self) -> Optional[Currency]:
        return self._state.get_currency(KINGDOM_POINT_UUID)


class Reward:
    def __init__(self, state: CacheState, data: RewardPayload) -> None:
        self._state = state
        self.type: ItemTypeID = try_enum(ItemTypeID, data['ItemTypeID'])
        self.id: str = data['ItemID']
        self.quantity: int = data['Quantity']

    def __repr__(self) -> str:
        return f'<Reward type={self.type!r} id={self.id!r} quantity={self.quantity!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Reward) and self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def item(self) -> Optional[RewardItem]:
        if self.type == ItemTypeID.agent:
            return self._state.get_agent(self.id)
        elif self.type == ItemTypeID.buddy_level:
            return self._state.get_buddy_level(self.id)
        elif self.type == ItemTypeID.contract:
            return self._state.get_contract(self.id)
        elif self.type == ItemTypeID.skin_level:
            return self._state.get_skin_level(self.id)
        elif self.type == ItemTypeID.skin_chroma:
            return self._state.get_skin_chroma(self.id)
        elif self.type == ItemTypeID.spray:
            return self._state.get_spray(self.id)
        elif self.type == ItemTypeID.spray_level:
            return self._state.get_spray_level(self.id)
        elif self.type == ItemTypeID.player_card:
            return self._state.get_player_card(self.id)
        elif self.type == ItemTypeID.player_title:
            return self._state.get_player_title(self.id)
        elif self.type == ItemTypeID.currency:
            return self._state.get_currency(self.id)
        else:
            _log.warning(f'Unknown reward type {self.type}')
            return None


class Offer:
    def __init__(self, state: CacheState, data: OfferPayload, item: Optional[Any] = None) -> None:
        self._state = state
        self.id: str = data['OfferID']
        self._is_direct_purchase: bool = data['IsDirectPurchase']
        self.cost: int = 0
        self.currency_id: Optional[str] = None
        for key, value in data['Cost'].items():
            self.currency_id = key
            self.cost = value
            break
        self.rewards: List[Reward] = [Reward(state, reward) for reward in data['Rewards']]
        self._item: Optional[Any] = item

    @property
    def item(self) -> Optional[Any]:
        return self._item

    def __repr__(self) -> str:
        return f'<Offer offer_id={self.id!r}>'

    def __int__(self) -> int:
        return self.cost

    def __bool__(self) -> bool:
        return self.is_direct_purchase()

    def is_direct_purchase(self) -> bool:
        """Returns if the offer is a direct purchase"""
        return self._is_direct_purchase

    @property
    def currency(self) -> Optional[Currency]:
        """Returns the currency for the offer"""
        if self.currency_id is None:
            return None
        return self._state.get_currency(self.currency_id)


class Offers:
    def __init__(self, state: CacheState, data: OffersPayload) -> None:
        self.offers: List[Offer] = [Offer(state, offer) for offer in data['Offers']]

    def __repr__(self) -> str:
        return f'<Offers offers={self.offers!r}>'


class Entitlements:
    def __init__(self, client: Client, data: EntitlementsPayload) -> None:
        self._client = client
        self._agents: List[Agent] = []
        self._skin_levels: List[SkinLevel] = []
        self._skin_chromas: List[SkinChroma] = []
        self._buddy_levels: List[BuddyLevel] = []
        self._sprays: List[Spray] = []
        self._player_cards: List[PlayerCard] = []
        self._player_titles: List[PlayerTitle] = []
        self._contracts: List[ContractValorantAPI] = []
        self.fill_items(data['EntitlementsByTypes'])

    # def __repr__(self) -> str:
    #     return f'<Entitlements> agents={len(self.agents)} skin_levels={len(self.skin_levels)} skin_chromas={len(self.skin_chromas)} buddy_levels={len(self.buddy_levels)} sprays={len(self.sprays)} player_cards={len(self.player_cards)} player_titles={len(self.player_titles)} contracts={len(self.contracts)}>'

    @property
    def agents(self) -> List[Agent]:
        return self._agents.copy()

    @property
    def skin_levels(self) -> List[SkinLevel]:
        return self._skin_levels.copy()

    @property
    def skin_chromas(self) -> List[SkinChroma]:
        return self._skin_chromas.copy()

    @property
    def buddy_levels(self) -> List[BuddyLevel]:
        return self._buddy_levels.copy()

    @property
    def sprays(self) -> List[Spray]:
        return self._sprays.copy()

    @property
    def player_cards(self) -> List[PlayerCard]:
        return self._player_cards.copy()

    @property
    def player_titles(self) -> List[PlayerTitle]:
        return self._player_titles.copy()

    @property
    def contracts(self) -> List[ContractValorantAPI]:
        return self._contracts.copy()

    def fill_items(self, data: List[EntitlementsByTypePayload]) -> None:
        for entitlement in data:
            item_type = try_enum(ItemTypeID, entitlement['ItemTypeID'])
            if item_type == ItemTypeID.agent:
                for item in entitlement['Entitlements']:
                    agent = self._client.valorant_api.get_agent(item['ItemID'])
                    if agent is None:
                        _log.warning(f'Unknown agent {item["ItemID"]}')
                        continue
                    self._agents.append(agent)
            elif item_type == ItemTypeID.buddy_level:
                for item in entitlement['Entitlements']:
                    buddy_level = self._client.valorant_api.get_buddy_level(item['ItemID'])
                    if buddy_level is None:
                        _log.warning(f'Unknown buddy level {item["ItemID"]}')
                        continue
                    self._buddy_levels.append(buddy_level)

            elif item_type == ItemTypeID.contract:
                for item in entitlement['Entitlements']:
                    contract = self._client.valorant_api.get_contract(item['ItemID'])
                    if contract is None:
                        _log.warning(f'Unknown contract {item["ItemID"]}')
                        continue
                    self._contracts.append(contract)

            elif item_type == ItemTypeID.skin_level:
                for item in entitlement['Entitlements']:
                    skin_level = self._client.valorant_api.get_skin_level(item['ItemID'])
                    if skin_level is None:
                        _log.warning(f'Unknown skin level {item["ItemID"]}')
                        continue
                    self._skin_levels.append(skin_level)

            elif item_type == ItemTypeID.skin_chroma:
                for item in entitlement['Entitlements']:
                    skin_chroma = self._client.valorant_api.get_skin_chroma(item['ItemID'])
                    if skin_chroma is None:
                        _log.warning(f'Unknown skin chroma {item["ItemID"]}')
                        continue
                    self._skin_chromas.append(skin_chroma)

            elif item_type == ItemTypeID.spray:
                for item in entitlement['Entitlements']:
                    spray = self._client.valorant_api.get_spray(item['ItemID'])
                    if spray is None:
                        _log.warning(f'Unknown spray {item["ItemID"]}')
                        continue
                    self._sprays.append(spray)

            elif item_type == ItemTypeID.player_card:
                for item in entitlement['Entitlements']:
                    player_card = self._client.valorant_api.get_player_card(item['ItemID'])
                    if player_card is None:
                        _log.warning(f'Unknown player card {item["ItemID"]}')
                        continue
                    self._player_cards.append(player_card)

            elif item_type == ItemTypeID.player_title:
                for item in entitlement['Entitlements']:
                    player_title = self._client.valorant_api.get_player_title(item['ItemID'])
                    if player_title is None:
                        _log.warning(f'Unknown player title {item["ItemID"]}')
                        continue
                    self._player_titles.append(player_title)
            else:
                _log.warning(f'Unknown item type {item_type}')

    async def refresh(self) -> None:
        data = await self._client.http.get_store_entitlements()
        self.fill_items(data['EntitlementsByTypes'])


class AccessoryStoreOffer:
    def __init__(self, state: CacheState, data: AccessoryStoreOfferPayload) -> None:
        self._state: CacheState = state
        self.offer: Offer = Offer(state, data['Offer'])
        self.contract_id: str = data['ContractID']
        self._contract: Optional[ContractValorantAPI] = self._state.get_contract(uuid=self.contract_id)

    @property
    def contract(self) -> Optional[ContractValorantAPI]:
        return self._contract


class AccessoryStore:
    def __init__(self, state: CacheState, data: AccessoryStorePayload) -> None:
        self.offers: List[AccessoryStoreOffer] = [
            AccessoryStoreOffer(state, offer) for offer in data['AccessoryStoreOffers']
        ]
        self.remaining_duration_in_seconds: int = data['AccessoryStoreRemainingDurationInSeconds']
        self.store_front_id: str = data['StorefrontID']

    @property
    def remaining_time_utc(self) -> datetime.datetime:
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=self.remaining_duration_in_seconds)

    def __repr__(self) -> str:
        return f'<AccessoryStore offers={self.offers} remaining_duration_in_seconds={self.remaining_duration_in_seconds} store_front_id={self.store_front_id}>'


class AgentStoreOffer:
    def __init__(self, client: Client, data: AgentStoreOfferPayload) -> None:
        self._client: Client = client
        self.agent_id: str = data['AgentID']
        self.store_offers: List[Offer] = [Offer(client.valorant_api.cache, offer) for offer in data['StoreOffers']]

    def __repr__(self) -> str:
        return f'<AgentStoreOffer agent={self.agent}>'

    @property
    def agent(self) -> Optional[Agent]:
        return self._client.valorant_api.get_agent(self.agent_id)


class AgentStore:
    def __init__(self, client: Client, data: AgentStorePayload) -> None:
        self._client: Client = client
        self.agent_store_offers: List[AgentStoreOffer] = [
            AgentStoreOffer(client, offer) for offer in data['AgentStoreOffers']
        ]
        self.featured_agent_id: str = data['FeaturedAgent']

    def __repr__(self) -> str:
        return f'<AgentStore featured_agent={self.featured_agent} agent_store_offers={self.agent_store_offers}>'

    def __hash__(self) -> int:
        return hash((self.featured_agent_id, tuple(self.agent_store_offers)))

    @property
    def featured_agent(self) -> Optional[Agent]:
        return self._client.valorant_api.get_agent(self.featured_agent_id)

    async def fetch_featured_agent_recruitment_progress(self) -> Optional[RecruitmentProgressUpdate]:
        contracts = await self._client.fetch_contracts()
        for processed_match in sorted(
            contracts.processed_matches,
            key=lambda x: x.recruitment_progress_update.progress_after if x.recruitment_progress_update else -1,
            reverse=True,
        ):
            if processed_match.recruitment_progress_update is None:
                continue
            if processed_match.recruitment_progress_update.group_id == self.featured_agent_id:
                return processed_match.recruitment_progress_update
        return None
