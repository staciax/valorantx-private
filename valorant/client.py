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

import asyncio
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Coroutine, Iterator, Mapping, Optional, Type, Union

from . import utils
from .assets import Assets
from .enums import Locale, QueueID
from .http import HTTPClient
from .models import (
    MMR,
    AccountXP,
    Agent,
    Buddy,
    BuddyLevel,
    Bundle,
    Ceremony,
    Collection,
    CompetitiveTier,
    Content,
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
    PatchNotes,
    PlayerCard,
    PlayerTitle,
    Season,
    Skin,
    SkinChroma,
    SkinLevel,
    Spray,
    SprayLevel,
    StoreFront,
    Theme,
    Version,
    Wallet,
    Weapon,
)

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

__all__ = ('Client',)

_log = logging.getLogger(__name__)

MISSING: Any = utils.MISSING


class Client:
    def __init__(self, *, locale: Union[Locale, str] = Locale.american_english) -> None:

        # http client
        self.http: HTTPClient = HTTPClient()

        # config
        self._closed: bool = False
        self._ready: bool = False
        self._version: Optional[Version] = None
        self._season: Optional[str] = None

        # locale
        self._locale: Union[Locale, str] = locale

        # assets
        self.assets: Assets = Assets(client=self, locale=locale)

    async def __aenter__(self) -> Self:
        # do something
        loop = asyncio.get_running_loop()
        self.loop = loop
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if not self.is_closed():
            await self.close()

    def activate(self) -> None:
        ...
        # self.version = self.http.get_valorant_version()
        # self.season = self.http.get_valorant_season()
        #  TODO: fetch version and season

    async def close(self) -> None:

        if self._closed:
            return
        self._closed = True
        await self.http.close()

    def is_closed(self) -> bool:
        return self._closed

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def version(self) -> Optional[Version]:
        return self._version

    @version.setter
    def version(self, value: Optional[Version]) -> None:
        self._version = value

    @locale.setter
    def locale(self, locale: str) -> None:
        self._locale = locale

    # assets

    def get_agent(self, uuid: str, **kwargs) -> Optional[Agent]:
        """Get an agent by UUID or Display Name."""
        data = self.assets.get_agent(uuid, **kwargs)
        return Agent(client=self, data=data) if data else None

    def get_buddy(self, uuid: str) -> Optional[Union[Buddy, BuddyLevel]]:
        """Get a buddy by UUID or Display Name."""
        data = self.assets.get_buddy(uuid)
        return Buddy(client=self, data=data) if data else self.get_buddy_level(uuid)

    def get_buddy_level(self, uuid: str) -> Optional[BuddyLevel]:
        """Get a buddy level by UUID or Display Name."""
        data = self.assets.get_buddy_level(uuid)
        return BuddyLevel(client=self, data=data) if data else None

    def get_bundle(self, uuid: str) -> Optional[Bundle]:
        """Get a bundle by UUID or Display Name."""
        data = self.assets.get_bundle(uuid)
        return Bundle(client=self, data=data) if data else None

    def get_ceremony(self, uuid: str) -> Optional[Ceremony]:
        """Get a ceremony by UUID."""
        data = self.assets.get_ceremony(uuid)
        return Ceremony(client=self, data=data) if data else None

    def get_competitive_tier(self, uuid: str) -> Optional[CompetitiveTier]:
        """Get a competitive tier by UUID."""
        data = self.assets.get_competitive_tier(uuid)
        return CompetitiveTier(client=self, data=data) if data else None

    def get_content_tier(self, uuid: str) -> Optional[ContentTier]:
        """Get a content tier by UUID."""
        data = self.assets.get_content_tier(uuid)
        return ContentTier(client=self, data=data) if data else None

    def get_contract(self, uuid: str) -> Optional[Contract]:
        """Get a contract by UUID."""
        data = self.assets.get_contract(uuid)
        return Contract(client=self, data=data) if data else None

    def get_currency(self, uuid: str) -> Optional[Currency]:
        """Get a currency by UUID."""
        data = self.assets.get_currency(uuid)
        return Currency(client=self, data=data) if data else None

    def get_event(self, uuid: str) -> Optional[Event]:
        """Get an event by UUID."""
        data = self.assets.get_event(uuid)
        return Event(client=self, data=data) if data else None

    def get_game_mode(self, uuid: str) -> Optional[GameMode]:
        """Get a game mode by UUID."""
        data = self.assets.get_game_mode(uuid)
        return GameMode(client=self, data=data) if data else None

    def get_game_mode_equippable(self, uuid: str) -> Optional[GameModeEquippable]:
        """Get a game mode equippable by UUID."""
        data = self.assets.get_game_mode_equippable(uuid)
        return GameModeEquippable(client=self, data=data) if data else None

    def get_gear(self, uuid: str) -> Optional[Gear]:
        """Get a gear by UUID."""
        data = self.assets.get_gear(uuid)
        return Gear(client=self, data=data) if data else None

    def get_level_border(self, uuid: str) -> Optional[LevelBorder]:
        """Get a level border by UUID."""
        data = self.assets.get_level_border(uuid)
        return LevelBorder(client=self, data=data) if data else None

    def get_map(self, uuid: str) -> Optional[Map]:
        """Get a map by UUID."""
        data = self.assets.get_map(uuid)
        return Map(client=self, data=data) if data else None

    def get_mission(self, uuid: str) -> Optional[Mission]:
        """missions, Get a mission by UUID."""
        data = self.assets.get_mission(uuid)
        return Mission(client=self, data=data) if data else None

    def get_player_card(self, uuid: str) -> Optional[PlayerCard]:
        """player_cards, Get a player card by UUID."""
        data = self.assets.get_player_card(uuid)
        return PlayerCard(client=self, data=data) if data else None

    def get_player_title(self, uuid: str) -> Optional[PlayerTitle]:
        """player_titles, Get a player title by UUID."""
        data = self.assets.get_player_title(uuid)
        return PlayerTitle(client=self, data=data) if data else None

    def get_season(self, uuid: str) -> Optional[Season]:
        """seasons, Get a season by UUID."""
        data = self.assets.get_season(uuid)
        return Season(client=self, data=data) if data else None

    def get_spray(self, uuid: str) -> Optional[Union[Spray, SprayLevel]]:
        """Get a spray by UUID."""
        data = self.assets.get_spray(uuid)
        return Spray(client=self, data=data) if data else self.get_spray_level(uuid)

    def get_spray_level(self, uuid: str) -> Optional[SprayLevel]:
        """Get a spray level by UUID."""
        data = self.assets.get_spray_level(uuid)
        return SprayLevel(client=self, data=data) if data else None

    def get_theme(self, uuid: str) -> Optional[Theme]:
        """themes, Get a theme by UUID."""
        data = self.assets.get_theme(uuid)
        return Theme(client=self, data=data) if data else None

    def get_weapon(self, uuid: str) -> Optional[Weapon]:
        """weapons, Get a weapon by UUID."""
        data = self.assets.get_weapon(uuid)
        return Weapon(client=self, data=data) if data else None

    def get_skin(self, uuid: str) -> Optional[Union[Skin, SkinLevel, SkinChroma]]:
        """weapon_skins, Get a weapon skin by UUID."""
        data = self.assets.get_skin(uuid)
        return Skin(client=self, data=data) if data else self.get_skin_level(uuid) or self.get_skin_chroma(uuid)

    def get_skin_level(self, uuid: str) -> Optional[SkinLevel]:
        """weapon_skins_levels, Get a weapon skin level by UUID."""
        data = self.assets.get_skin_level(uuid)
        return SkinLevel(client=self, data=data) if data else None

    def get_skin_chroma(self, uuid: str) -> Optional[SkinChroma]:
        """weapon_skins_chromas, Get a weapon skin chroma by UUID."""
        data = self.assets.get_skin_chroma(uuid)
        return SkinChroma(client=self, data=data) if data else None

    def get_all_bundles(self) -> Iterator[Bundle]:
        data = self.assets.get_asset('bundles')
        for item in data.values():
            yield Bundle(client=self, data=item)

    # PVP endpoints

    def fetch_game_content(self) -> Content:
        return Content(client=self, data=self.http.fetch_content())

    async def fetch_account_xp(self) -> AccountXP:
        data = await self.http.fetch_account_xp()
        return AccountXP(client=self, data=data)

    async def fetch_player_loadout(self) -> Collection:
        # ensure
        # account_xp = await self.fetch_account_xp()
        # self.user._account_level = account_xp.progress['Level']  # TODO: models.User.account_level
        data = await self.http.fetch_player_loadout()
        return Collection(client=self, data=data)

    def put_player_loadout(self, loadout: Mapping) -> Coroutine[Any, Any, None]:
        return self.http.put_player_loadout(loadout)

    async def fetch_player_mmr(self, puuid: Optional[str] = None) -> MMR:
        data = await self.http.fetch_mmr(puuid)
        return MMR(client=self, data=data)

    # async def fetch_player_match_history(
    #     self,
    #     puuid: Optional[str] = None,
    #     start_index: int = 0,
    #     end_index: int = 15,
    #     queue_id: Optional[str, QueueID] = QueueID.unrated,
    # ) -> FetchMatchHistory:
    #     data = await self.http.fetch_match_history(puuid, start_index, end_index, queue_id)
    #     return FetchMatchHistory(client=self, data=data)

    # async def fetch_match_details(self, match_id: str) -> Any:
    #     match_details = await self.http.fetch_match_details(match_id)
    #     return MatchDetail(client=self, data=match_details)

    # store endpoints

    async def fetch_store_front(self) -> StoreFront:
        data = await self.http.store_fetch_storefront()
        return StoreFront(client=self, data=data)

    async def fetch_wallet(self) -> Wallet:
        data = await self.http.store_fetch_wallet()
        return Wallet(client=self, data=data)

    async def fetch_patch_notes(self, locale: Union[str, Locale] = Locale.american_english) -> PatchNotes:
        data = await self.http.fetch_patch_notes(locale)
        return PatchNotes(client=self, data=data, locale=locale)

    # asset

    async def fetch_all_assets(self, force: bool = False) -> None:
        await self.assets.fetch_all_assets(force=force)

    async def get_valorant_version(self) -> Version:
        data = await self.http.asset_valorant_version()
        return Version(client=self, data=data)
