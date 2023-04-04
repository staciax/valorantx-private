import asyncio
from typing import List, Optional

import aiohttp

from ..utils import MISSING
from .cache import CacheState
from .enums import Locale
from .http import HTTPClient
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


class Client:
    def __init__(self, session: aiohttp.ClientSession, locale: Locale = Locale.english) -> None:
        self._http: HTTPClient = HTTPClient(session)
        self._cache: CacheState = CacheState(locale=locale, http=self._http)
        self._ready: asyncio.Event = MISSING
        self._closed: bool = False

    async def init(self) -> None:
        self._ready = asyncio.Event()

        await self._cache.init()

        self._ready.set()

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self._http.close()

    def clear(self) -> None:
        self._closed = False
        self._ready.clear()
        self._ready = MISSING
        self._cache.clear()

    async def wait_until_ready(self) -> None:
        if self._ready is not MISSING:
            await self._ready.wait()
        else:
            raise RuntimeError('Client not initialized yet.')

    # agents

    @property
    def agents(self) -> List[Agent]:
        return self._cache.agents

    def get_agent(self, uuid: str) -> Optional[Agent]:
        return self._cache.get_agent(uuid)

    # buddies

    @property
    def buddies(self) -> List[Buddy]:
        return self._cache.buddies

    @property
    def buddy_levels(self) -> List[BuddyLevel]:
        return self._cache.buddy_levels

    def get_buddy(self, uuid: str) -> Optional[Buddy]:
        return self._cache.get_buddy(uuid)

    def get_buddy_level(self, uuid: str) -> Optional[BuddyLevel]:
        return self._cache.get_buddy_level(uuid)

    # bundles

    @property
    def bundles(self) -> List[Bundle]:
        return self._cache.bundles

    def get_bundle(self, uuid: str) -> Optional[Bundle]:
        return self._cache.get_bundle(uuid)

    # ceremonies

    @property
    def ceremonies(self) -> List[Ceremony]:
        return self._cache.ceremonies

    def get_ceremony(self, uuid: str) -> Optional[Ceremony]:
        return self._cache.get_ceremony(uuid)

    # competitive_tiers

    @property
    def competitive_tiers(self) -> List[CompetitiveTier]:
        return self._cache.competitive_tiers

    def get_competitive_tier(self, uuid: str) -> Optional[CompetitiveTier]:
        return self._cache.get_competitive_tier(uuid)

    # content_tiers

    @property
    def content_tiers(self) -> List[ContentTier]:
        return self._cache.content_tiers

    def get_content_tier(self, uuid: str) -> Optional[ContentTier]:
        return self._cache.get_content_tier(uuid)

    # contracts

    @property
    def contracts(self) -> List[Contract]:
        return self._cache.contracts

    def get_contract(self, uuid: str) -> Optional[Contract]:
        return self._cache.get_contract(uuid)

    # currencies

    @property
    def currencies(self) -> List[Currency]:
        return self._cache.currencies

    def get_currency(self, uuid: str) -> Optional[Currency]:
        return self._cache.get_currency(uuid)

    # events

    @property
    def events(self) -> List[Event]:
        return self._cache.events

    def get_event(self, uuid: str) -> Optional[Event]:
        return self._cache.get_event(uuid)

    # game_modes

    @property
    def game_modes(self) -> List[GameMode]:
        return self._cache.game_modes

    @property
    def game_mode_equippables(self) -> List[GameModeEquippable]:
        return self._cache.game_mode_equippables

    def get_game_mode(self, uuid: str) -> Optional[GameMode]:
        return self._cache.get_game_mode(uuid)

    def get_game_mode_equippable(self, uuid: str) -> Optional[GameModeEquippable]:
        return self._cache.get_game_mode_equippable(uuid)
