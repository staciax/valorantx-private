from __future__ import annotations

import asyncio

# import json
# import os
from typing import TYPE_CHECKING, Dict, List, Optional  # Any, Callable, Coroutine,

from .models import (
    Agent,
    Buddy,
    BuddyLevel,
    Bundle,
    Ceremony,
    CompetitiveTier,
    ContentTier,
    Contract,
    Currency,
    Event,
    GameMode,
    GameModeEquippable,
)

if TYPE_CHECKING:
    from ..enums import Locale
    from .http import HTTPClient
    from .types import (
        agents,
        buddies,
        bundles,
        ceremonies,
        competitive_tiers,
        content_tiers,
        contracts,
        currencies,
        events,
        gamemodes,
    )

# class BaseCache(ABC):

#     @abstractmethod
#     def get(self):
#         raise NotImplementedError

#     @abstractmethod
#     def find(self):
#         raise NotImplementedError


class CacheState:
    def __init__(self, *, locale: Locale, http: HTTPClient, to_file: bool = False) -> None:
        self.locale = locale
        self.http = http
        self.cache: bool = True
        self._to_file: bool = to_file

        self._agents: Dict[str, Agent] = {}
        self._buddies: Dict[str, Buddy] = {}
        self._buddy_levels: Dict[str, BuddyLevel] = {}
        self._bundles: Dict[str, Bundle] = {}
        self._ceremonies: Dict[str, Ceremony] = {}
        self._competitive_tiers: Dict[str, CompetitiveTier] = {}
        self._content_tiers: Dict[str, ContentTier] = {}
        self._contracts: Dict[str, Contract] = {}
        self._currencies: Dict[str, Currency] = {}
        self._events: Dict[str, Event] = {}
        self._game_modes: Dict[str, GameMode] = {}
        self._game_mode_equippables: Dict[str, GameModeEquippable] = {}

    async def init(self) -> None:
        tasks = [
            self.http.get_agents,
            self.http.get_buddies,
            self.http.get_bundles,
            self.http.get_ceremonies,
            self.http.get_competitive_tiers,
            self.http.get_content_tiers,
            self.http.get_contracts,
            self.http.get_currencies,
            self.http.get_events,
            self.http.get_game_modes,
            self.http.get_game_mode_equippables,
            # self.http.get_gear,
            # self.http.get_level_borders,
            # self.http.get_maps,
            # self.http.get_player_cards,
            # self.http.get_player_titles,
            # self.http.get_seasons,
            # self.http.get_sprays,
            # self.http.get_themes,
            # self.http.get_weapons,
            # self.http.get_version,
        ]
        # if self._to_file:

        #     # read from file
        #     for func in tasks:
        #         funcname = func.__name__.split('_')[1:]
        #         filename = '_'.join(funcname) + '.json'
        #         # add_to_cache = getattr(self, f'add_{funcname}')
        #         # if os.path.exists(filename):
        #         #     with open(filename, 'r') as f:
        #         #         data = json.load(f)
        #         #         continue
        #         # else:
        #         #     data = await func()
        #         #     self._add_to_file(data, filename)
        #         # add_to_cache = getattr(self, f'add_{funcname}')
        # else:
        # results = await self._fetch_data_from_api(tasks)

        results = await asyncio.gather(*[task() for task in tasks])
        for func, result in zip(tasks, results):
            assert result is not None
            funcname = func.__name__.split('_')[1:]
            funcname = '_'.join(funcname)
            parse_func = getattr(self, f'_add_{funcname}')
            parse_func(result)

    # async def _fetch_data_from_api(self, tasks: List[Callable[..., Coroutine[Any, Any, Any]]]) -> List[Any]:
    #     results = await asyncio.gather(*[task() for task in tasks])
    #     return results
    # for func, result in zip(tasks, results):
    #     assert result is not None
    #     funcname = func.__name__.split('_')[1:]
    #     funcname = '_'.join(funcname)
    #     parse_func = getattr(self, f'add_{funcname}')
    #     parse_func(result)

    # def _add_to_file(self, data: Any, filename: str) -> None:
    #     with open(filename, 'w') as f:
    #         json.dump(data, f, indent=4)

    def clear(self) -> None:
        self._agents.clear()
        self._buddies.clear()
        self._buddy_levels.clear()
        self._bundles.clear()
        self._ceremonies.clear()
        self._competitive_tiers.clear()
        self._content_tiers.clear()
        self._contracts.clear()
        self._currencies.clear()
        self._events.clear()
        self._game_modes.clear()
        self._game_mode_equippables.clear()

    # agents

    @property
    def agents(self) -> List[Agent]:
        return list(self._agents.values())

    def get_agent(self, uuid: Optional[str]) -> Optional[Agent]:
        return self._agents.get(uuid)  # type: ignore

    def store_agent(self, data: agents.Agent) -> Agent:
        agent_id = data['uuid']
        self._agents[agent_id] = agent = Agent(state=self, data=data)
        return agent

    def _add_agents(self, data: agents.Agents) -> None:
        agent_data = data['data']
        for agent in agent_data:
            existing = self.get_agent(agent['uuid'])
            if existing is None:
                self.store_agent(agent)

    # buddies

    @property
    def buddies(self) -> List[Buddy]:
        return list(self._buddies.values())

    @property
    def buddy_levels(self) -> List[BuddyLevel]:
        return list(self._buddy_levels.values())

    def get_buddy(self, uuid: Optional[str]) -> Optional[Buddy]:
        return self._buddies.get(uuid)  # type: ignore

    def get_buddy_level(self, uuid: Optional[str]) -> Optional[BuddyLevel]:
        return self._buddy_levels.get(uuid)  # type: ignore

    def store_buddy(self, data: buddies.Buddy) -> Buddy:
        buddy_id = data['uuid']
        self._buddies[buddy_id] = buddy = Buddy(state=self, data=data)
        return buddy

    def store_buddy_level(self, data: buddies.BuddyLevel) -> BuddyLevel:
        buddy_level_id = data['uuid']
        self._buddy_levels[buddy_level_id] = buddy_level = BuddyLevel(state=self, data=data)
        return buddy_level

    def _add_buddies(self, data: buddies.Buddies) -> None:
        buddy_data = data['data']
        for buddy in buddy_data:
            buddy_existing = self.get_buddy(buddy['uuid'])
            if buddy_existing is None:
                buddy_existing = self.store_buddy(buddy)
            for level in buddy['levels']:
                level_existing = self.get_buddy_level(level['uuid'])
                if level_existing is None:
                    level_existing = self.store_buddy_level(level)
                level_existing.buddy = buddy_existing

    # bundles

    @property
    def bundles(self) -> List[Bundle]:
        return list(self._bundles.values())

    def get_bundle(self, uuid: Optional[str]) -> Optional[Bundle]:
        return self._bundles.get(uuid)  # type: ignore

    def store_bundle(self, data: bundles.Bundle) -> Bundle:
        bundle_id = data['uuid']
        self._bundles[bundle_id] = bundle = Bundle(state=self, data=data)
        return bundle

    def _add_bundles(self, data: bundles.Bundles) -> None:
        bundle_data = data['data']
        for bundle in bundle_data:
            bundle_existing = self.get_bundle(bundle['uuid'])
            if bundle_existing is None:
                bundle_existing = self.store_bundle(bundle)

    # ceremonies

    @property
    def ceremonies(self) -> List[Ceremony]:
        return list(self._ceremonies.values())

    def get_ceremony(self, uuid: Optional[str]) -> Optional[Ceremony]:
        return self._ceremonies.get(uuid)  # type: ignore

    def store_ceremony(self, data: ceremonies.Ceremony) -> Ceremony:
        ceremony_id = data['uuid']
        self._ceremonies[ceremony_id] = ceremony = Ceremony(state=self, data=data)
        return ceremony

    def _add_ceremonies(self, data: ceremonies.Ceremonies) -> None:
        ceremony_data = data['data']
        for ceremony in ceremony_data:
            ceremony_existing = self.get_ceremony(ceremony['uuid'])
            if ceremony_existing is None:
                ceremony_existing = self.store_ceremony(ceremony)

    # competitive tiers

    @property
    def competitive_tiers(self) -> List[CompetitiveTier]:
        return list(self._competitive_tiers.values())

    def get_competitive_tier(self, uuid: Optional[str]) -> Optional[CompetitiveTier]:
        return self._competitive_tiers.get(uuid)  # type: ignore

    def store_competitive_tier(self, data: competitive_tiers.CompetitiveTier) -> CompetitiveTier:
        competitive_tier_id = data['uuid']
        self._competitive_tiers[competitive_tier_id] = competitive_tier = CompetitiveTier(state=self, data=data)
        return competitive_tier

    def _add_competitive_tiers(self, data: competitive_tiers.CompetitiveTiers) -> None:
        competitive_tier_data = data['data']
        for competitive_tier in competitive_tier_data:
            competitive_tier_existing = self.get_competitive_tier(competitive_tier['uuid'])
            if competitive_tier_existing is None:
                competitive_tier_existing = self.store_competitive_tier(competitive_tier)

    # content tiers

    @property
    def content_tiers(self) -> List[ContentTier]:
        return list(self._content_tiers.values())

    def get_content_tier(self, uuid: Optional[str]) -> Optional[ContentTier]:
        return self._content_tiers.get(uuid)  # type: ignore

    def store_content_tier(self, data: content_tiers.ContentTier) -> ContentTier:
        content_tier_id = data['uuid']
        self._content_tiers[content_tier_id] = content_tier = ContentTier(state=self, data=data)
        return content_tier

    def _add_content_tiers(self, data: content_tiers.ContentTiers) -> None:
        content_tier_data = data['data']
        for content_tier in content_tier_data:
            content_tier_existing = self.get_content_tier(content_tier['uuid'])
            if content_tier_existing is None:
                content_tier_existing = self.store_content_tier(content_tier)

    # contracts

    @property
    def contracts(self) -> List[Contract]:
        return list(self._contracts.values())

    def get_contract(self, uuid: Optional[str]) -> Optional[Contract]:
        return self._contracts.get(uuid)  # type: ignore

    def store_contract(self, data: contracts.Contract) -> Contract:
        contract_id = data['uuid']
        self._contracts[contract_id] = contract = Contract(state=self, data=data)
        return contract

    def _add_contracts(self, data: contracts.Contracts) -> None:
        contract_data = data['data']
        for contract in contract_data:
            contract_existing = self.get_contract(contract['uuid'])
            if contract_existing is None:
                contract_existing = self.store_contract(contract)

    # currencies

    @property
    def currencies(self) -> List[Currency]:
        return list(self._currencies.values())

    def get_currency(self, uuid: Optional[str]) -> Optional[Currency]:
        return self._currencies.get(uuid)  # type: ignore

    def store_currency(self, data: currencies.Currency) -> Currency:
        currency_id = data['uuid']
        self._currencies[currency_id] = currency = Currency(state=self, data=data)
        return currency

    def _add_currencies(self, data: currencies.Currencies) -> None:
        currency_data = data['data']
        for currency in currency_data:
            currency_existing = self.get_currency(currency['uuid'])
            if currency_existing is None:
                currency_existing = self.store_currency(currency)

    # events

    @property
    def events(self) -> List[Event]:
        return list(self._events.values())

    def get_event(self, uuid: Optional[str]) -> Optional[Event]:
        return self._events.get(uuid)  # type: ignore

    def store_event(self, data: events.Event) -> Event:
        event_id = data['uuid']
        self._events[event_id] = event = Event(state=self, data=data)
        return event

    def _add_events(self, data: events.Events) -> None:
        event_data = data['data']
        for event in event_data:
            event_existing = self.get_event(event['uuid'])
            if event_existing is None:
                event_existing = self.store_event(event)

    # game modes

    @property
    def game_modes(self) -> List[GameMode]:
        return list(self._game_modes.values())

    @property
    def game_mode_equippables(self) -> List[GameModeEquippable]:
        return list(self._game_mode_equippables.values())

    def get_game_mode(self, uuid: Optional[str]) -> Optional[GameMode]:
        return self._game_modes.get(uuid)  # type: ignore

    def get_game_mode_equippable(self, uuid: Optional[str]) -> Optional[GameModeEquippable]:
        return self._game_mode_equippables.get(uuid)  # type: ignore

    def store_game_mode(self, data: gamemodes.GameMode) -> GameMode:
        game_mode_id = data['uuid']
        self._game_modes[game_mode_id] = game_mode = GameMode(state=self, data=data)
        return game_mode

    def store_game_mode_equippable(self, data: gamemodes.GameModeEquippable) -> GameModeEquippable:
        game_mode_equippable_id = data['uuid']
        self._game_mode_equippables[game_mode_equippable_id] = game_mode_equippable = GameModeEquippable(
            state=self, data=data
        )
        return game_mode_equippable

    def _add_game_modes(self, data: gamemodes.GameModes) -> None:
        game_mode_data = data['data']
        for game_mode in game_mode_data:
            game_mode_existing = self.get_game_mode(game_mode['uuid'])
            if game_mode_existing is None:
                game_mode_existing = self.store_game_mode(game_mode)

    def _add_game_mode_equippables(self, data: gamemodes.GameModeEquippables) -> None:
        game_mode_equippable_data = data['data']
        for game_mode_equippable in game_mode_equippable_data:
            game_mode_equippable_existing = self.get_game_mode_equippable(game_mode_equippable['uuid'])
            if game_mode_equippable_existing is None:
                game_mode_equippable_existing = self.store_game_mode_equippable(game_mode_equippable)
