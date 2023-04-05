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
    CompetitiveSeason,
    CompetitiveTier,
    ContentTier,
    Contract,
    Currency,
    Event,
    GameMode,
    GameModeEquippable,
    Gear,
    LevelBorder,
    Map,
    Mission,
    PlayerCard,
    PlayerTitle,
    Season,
    Skin,
    SkinChroma,
    SkinLevel,
    Spray,
    SprayLevel,
    Theme,
    Version,
    Weapon,
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

    async def fetch_agent(
        self, uuid: str, *, language: Optional[Locale] = None, is_playable_character: bool = True
    ) -> Agent:
        language = language or self._cache.locale
        data = await self._http.get_agent(uuid, language=language.value, is_playable_character=is_playable_character)
        return Agent(state=self._cache, data=data['data'])

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

    async def fetch_buddy(self, uuid: str, *, language: Optional[Locale] = None) -> Buddy:
        data = await self._http.get_buddy(uuid, language=self._language(language))
        return Buddy(state=self._cache, data=data['data'])

    async def fetch_buddy_level(self, uuid: str, *, language: Optional[Locale] = None) -> BuddyLevel:
        data = await self._http.get_buddy_level(uuid, language=self._language(language))
        return BuddyLevel(state=self._cache, data=data['data'])

    # bundles

    @property
    def bundles(self) -> List[Bundle]:
        return self._cache.bundles

    def get_bundle(self, uuid: str) -> Optional[Bundle]:
        return self._cache.get_bundle(uuid)

    async def fetch_bundle(self, uuid: str, *, language: Optional[Locale] = None) -> Bundle:
        data = await self._http.get_bundle(uuid, language=self._language(language))
        return Bundle(state=self._cache, data=data['data'])

    # ceremonies

    @property
    def ceremonies(self) -> List[Ceremony]:
        return self._cache.ceremonies

    def get_ceremony(self, uuid: str) -> Optional[Ceremony]:
        return self._cache.get_ceremony(uuid)

    async def fetch_ceremony(self, uuid: str, *, language: Optional[Locale] = None) -> Ceremony:
        data = await self._http.get_ceremony(uuid, language=self._language(language))
        return Ceremony(state=self._cache, data=data['data'])

    # competitive_tiers

    @property
    def competitive_tiers(self) -> List[CompetitiveTier]:
        return self._cache.competitive_tiers

    def get_competitive_tier(self, uuid: str) -> Optional[CompetitiveTier]:
        return self._cache.get_competitive_tier(uuid)

    async def fetch_competitive_tier(self, uuid: str, *, language: Optional[Locale] = None) -> CompetitiveTier:
        data = await self._http.get_competitive_tier(uuid, language=self._language(language))
        return CompetitiveTier(state=self._cache, data=data['data'])

    # content_tiers

    @property
    def content_tiers(self) -> List[ContentTier]:
        return self._cache.content_tiers

    def get_content_tier(self, uuid: str) -> Optional[ContentTier]:
        return self._cache.get_content_tier(uuid)

    async def fetch_content_tier(self, uuid: str, *, language: Optional[Locale] = None) -> ContentTier:
        data = await self._http.get_content_tier(uuid, language=self._language(language))
        return ContentTier(state=self._cache, data=data['data'])

    # contracts

    @property
    def contracts(self) -> List[Contract]:
        return self._cache.contracts

    def get_contract(self, uuid: str) -> Optional[Contract]:
        return self._cache.get_contract(uuid)

    async def fetch_contract(self, uuid: str, *, language: Optional[Locale] = None) -> Contract:
        data = await self._http.get_contract(uuid, language=self._language(language))
        return Contract(state=self._cache, data=data['data'])

    # currencies

    @property
    def currencies(self) -> List[Currency]:
        return self._cache.currencies

    def get_currency(self, uuid: str) -> Optional[Currency]:
        return self._cache.get_currency(uuid)

    async def fetch_currency(self, uuid: str, *, language: Optional[Locale] = None) -> Currency:
        data = await self._http.get_currency(uuid, language=self._language(language))
        return Currency(state=self._cache, data=data['data'])

    # events

    @property
    def events(self) -> List[Event]:
        return self._cache.events

    def get_event(self, uuid: str) -> Optional[Event]:
        return self._cache.get_event(uuid)

    async def fetch_event(self, uuid: str, *, language: Optional[Locale] = None) -> Event:
        data = await self._http.get_event(uuid, language=self._language(language))
        return Event(state=self._cache, data=data['data'])

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

    async def fetch_game_mode(self, uuid: str, *, language: Optional[Locale] = None) -> GameMode:
        data = await self._http.get_game_mode(uuid, language=self._language(language))
        return GameMode(state=self._cache, data=data['data'])

    async def fetch_game_mode_equippable(self, uuid: str, *, language: Optional[Locale] = None) -> GameModeEquippable:
        data = await self._http.get_game_mode_equippable(uuid, language=self._language(language))
        return GameModeEquippable(state=self._cache, data=data['data'])

    # gear

    @property
    def gear(self) -> List[Gear]:
        return self._cache.gear

    def get_gear(self, uuid: str) -> Optional[Gear]:
        return self._cache.get_gear(uuid)

    async def fetch_gear(self, uuid: str, *, language: Optional[Locale] = None) -> Gear:
        data = await self._http.get_gear_(uuid, language=self._language(language))
        return Gear(state=self._cache, data=data['data'])

    # level_borders

    @property
    def level_borders(self) -> List[LevelBorder]:
        return self._cache.level_borders

    def get_level_border(self, uuid: str) -> Optional[LevelBorder]:
        return self._cache.get_level_border(uuid)

    async def fetch_level_border(self, uuid: str) -> LevelBorder:
        data = await self._http.get_level_border(uuid)
        return LevelBorder(state=self._cache, data=data['data'])

    # maps

    @property
    def maps(self) -> List[Map]:
        return self._cache.maps

    def get_map(self, uuid: str) -> Optional[Map]:
        return self._cache.get_map(uuid)

    async def fetch_map(self, uuid: str, *, language: Optional[Locale] = None) -> Map:
        data = await self._http.get_map(uuid, language=self._language(language))
        return Map(state=self._cache, data=data['data'])

    # missions

    @property
    def missions(self) -> List[Mission]:
        return self._cache.missions

    def get_mission(self, uuid: str) -> Optional[Mission]:
        return self._cache.get_mission(uuid)

    async def fetch_mission(self, uuid: str, *, language: Optional[Locale] = None) -> Mission:
        data = await self._http.get_mission(uuid, language=self._language(language))
        return Mission(state=self._cache, data=data['data'])

    # player_cards

    @property
    def player_cards(self) -> List[PlayerCard]:
        return self._cache.player_cards

    def get_player_card(self, uuid: str) -> Optional[PlayerCard]:
        return self._cache.get_player_card(uuid)

    async def fetch_player_card(self, uuid: str, *, language: Optional[Locale] = None) -> PlayerCard:
        data = await self._http.get_player_card(uuid, language=self._language(language))
        return PlayerCard(state=self._cache, data=data['data'])

    # player_titles

    @property
    def player_titles(self) -> List[PlayerTitle]:
        return self._cache.player_titles

    def get_player_title(self, uuid: str) -> Optional[PlayerTitle]:
        return self._cache.get_player_title(uuid)

    async def fetch_player_title(self, uuid: str, *, language: Optional[Locale] = None) -> PlayerTitle:
        data = await self._http.get_player_title(uuid, language=self._language(language))
        return PlayerTitle(state=self._cache, data=data['data'])

    # seasons

    @property
    def seasons(self) -> List[Season]:
        return self._cache.seasons

    def get_season(self, uuid: str) -> Optional[Season]:
        return self._cache.get_season(uuid)

    async def fetch_season(self, uuid: str, *, language: Optional[Locale] = None) -> Season:
        data = await self._http.get_season(uuid, language=self._language(language))
        return Season(state=self._cache, data=data['data'])

    @property
    def competitive_seasons(self) -> List[CompetitiveSeason]:
        return list(self._cache.competitive_seasons)

    def get_competitive_season(self, uuid: str) -> Optional[CompetitiveSeason]:
        return self._cache.get_competitive_season(uuid)

    async def fetch_competitive_season(self, uuid: str) -> CompetitiveSeason:
        data = await self._http.get_competitive_season(uuid)
        return CompetitiveSeason(state=self._cache, data=data['data'])

    # sprays

    @property
    def sprays(self) -> List[Spray]:
        return self._cache.sprays

    def get_spray(self, uuid: str) -> Optional[Spray]:
        return self._cache.get_spray(uuid)

    async def fetch_spray(self, uuid: str, *, language: Optional[Locale] = None) -> Spray:
        data = await self._http.get_spray(uuid, language=self._language(language))
        return Spray(state=self._cache, data=data['data'])

    @property
    def spray_levels(self) -> List[SprayLevel]:
        return self._cache.spray_levels

    def get_spray_level(self, uuid: str) -> Optional[SprayLevel]:
        return self._cache.get_spray_level(uuid)

    async def fetch_spray_level(self, uuid: str) -> SprayLevel:
        data = await self._http.get_spray_level(uuid)
        return SprayLevel(state=self._cache, data=data['data'])

    # themes

    @property
    def themes(self) -> List[Theme]:
        return self._cache.themes

    def get_theme(self, uuid: str) -> Optional[Theme]:
        return self._cache.get_theme(uuid)

    async def fetch_theme(self, uuid: str, *, language: Optional[Locale] = None) -> Theme:
        data = await self._http.get_theme(uuid, language=self._language(language))
        return Theme(state=self._cache, data=data['data'])

    # version

    @property
    def version(self) -> Version:
        return self._cache.version

    async def fetch_version(self) -> Version:
        data = await self._http.get_version()
        return Version(state=self._cache, data=data['data'])

    # weapons

    @property
    def weapons(self) -> List[Weapon]:
        return self._cache.weapons

    def get_weapon(self, uuid: str) -> Optional[Weapon]:
        return self._cache.get_weapon(uuid)

    async def fetch_weapon(self, uuid: str, *, language: Optional[Locale] = None) -> Weapon:
        data = await self._http.get_weapon(uuid, language=self._language(language))
        return Weapon(state=self._cache, data=data['data'])

    @property
    def skins(self) -> List[Skin]:
        return self._cache.skins

    def get_skin(self, uuid: str) -> Optional[Skin]:
        return self._cache.get_skin(uuid)

    async def fetch_skin(self, uuid: str, *, language: Optional[Locale] = None) -> Skin:
        data = await self._http.get_weapon_skin(uuid, language=self._language(language))
        return Skin(state=self._cache, data=data['data'])

    @property
    def skin_chromas(self) -> List[SkinChroma]:
        return self._cache.skin_chromas

    def get_skin_chroma(self, uuid: str) -> Optional[SkinChroma]:
        return self._cache.get_skin_chroma(uuid)

    async def fetch_skin_chroma(self, uuid: str, *, language: Optional[Locale] = None) -> SkinChroma:
        data = await self._http.get_weapon_skin_chroma(uuid, language=self._language(language))
        return SkinChroma(state=self._cache, data=data['data'])

    @property
    def skin_levels(self) -> List[SkinLevel]:
        return self._cache.skin_levels

    def get_skin_level(self, uuid: str) -> Optional[SkinLevel]:
        return self._cache.get_skin_level(uuid)

    async def fetch_skin_level(self, uuid: str, *, language: Optional[Locale] = None) -> SkinLevel:
        data = await self._http.get_weapon_skin_level(uuid, language=self._language(language))
        return SkinLevel(state=self._cache, data=data['data'])

    # helpers

    def _language(self, language: Optional[Locale]) -> Optional[str]:
        if language is None:
            # return self._cache.locale.value
            return None
        return language.value
