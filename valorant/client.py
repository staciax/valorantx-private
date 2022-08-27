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
import logging
from typing import TYPE_CHECKING, Any, Coroutine, Iterator, Mapping, Optional, Type, Union

from . import utils
from .assets import Assets
from .enums import Locale, QueueID, try_enum
from .errors import AuthRequired
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
    MatchDetails,
    MatchHistory,
    Mission,
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
from .models.patchnote import PatchNotes

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

# fmt: off
__all__ = (
    'Client',
)
# fmt: on

_log = logging.getLogger(__name__)

MISSING: Any = utils.MISSING


def _authorize_required(func):
    def wrapper(self: Client, *args: Any, **kwargs: Any) -> Any:
        if not self.is_authorized():
            client_func = f'Client.{func.__name__}'
            raise AuthRequired(f"{client_func!r} requires authorization")
        return func(self, *args, **kwargs)

    return wrapper


class Client:
    def __init__(self, *, locale: Union[Locale, str] = Locale.american_english, auto_fetch_assets: bool = True) -> None:

        self._locale: Union[Locale, str] = locale
        self._auto_fetch_assets: bool = auto_fetch_assets

        # config
        self._closed: bool = False
        self._ready: bool = False
        self._version: Optional[Version] = None
        self._season: Optional[Season] = None

        self._is_authorized: bool = False

        # http client
        self._http: HTTPClient = HTTPClient()

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

    async def authorize(self, username: Optional[str], password: Optional[str]) -> None:
        """Authorize the client with the given username and password."""
        #  TODO: fetch version and season

        self._is_authorized = True
        await self.http.static_login(username.strip(), password.strip())

    def is_authorized(self) -> bool:
        """Check if the client is authorized."""
        return self._is_authorized

    # def run(self, username: Optional[str], password: Optional[str]) -> None:
    #     async def runner():
    #         async with self:
    #             await self.login(username, password)
    #
    #     try:
    #         asyncio.run(runner())
    #     except KeyboardInterrupt:
    #         # nothing to do here
    #         # `asyncio.run` handles the loop cleanup
    #         # and `self.start` closes all sockets and the HTTPClient instance.
    #         return

    async def close(self) -> None:

        if self._closed:
            return
        self._closed = True
        await self.http.close()

    def is_closed(self) -> bool:
        return self._closed

    @property
    def http(self) -> HTTPClient:
        return self._http

    @http.setter
    def http(self, http: HTTPClient) -> None:
        self._http = http

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def version(self) -> Optional[Version]:
        return self._version

    @version.setter
    def version(self, value: Optional[Version]) -> None:
        self._version = value

    @property
    def season(self) -> Optional[Season]:
        return self._season

    @season.setter
    def season(self, value: Optional[Season]) -> None:
        self._season = value

    @locale.setter
    def locale(self, locale: str) -> None:
        self._locale = locale

    # assets

    async def fetch_all_assets(self, force: bool = False) -> None:
        await self.assets.fetch_all_assets(force=force)

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

    async def get_valorant_version(self) -> Version:
        data = await self.http.asset_valorant_version()
        return Version(client=self, data=data)

    # patch notes

    async def fetch_patch_notes(self, locale: Union[str, Locale] = Locale.american_english) -> PatchNotes:

        if isinstance(locale, str):
            locale = try_enum(Locale, str(locale))

        # endpoint is not available for simplified chinese
        if locale is Locale.chinese_simplified:
            locale = Locale.chinese_traditional
        data = await self.http.fetch_patch_notes(locale)

        return PatchNotes(client=self, data=data, locale=locale)

    # PVP endpoints

    @_authorize_required
    async def fetch_content(self) -> Content:
        data = await self.http.fetch_content()
        return Content(client=self, data=data)

    @_authorize_required
    async def fetch_account_xp(self) -> AccountXP:
        data = await self.http.fetch_account_xp()
        return AccountXP(client=self, data=data)

    @_authorize_required
    async def fetch_player_loadout(self, *, fetch_account_xp: bool = True) -> Collection:
        # ensure
        if fetch_account_xp:
            account_xp = await self.fetch_account_xp()
            # self.user._account_level = account_xp.level
        data = await self.http.fetch_player_loadout()
        return Collection(client=self, data=data)

    @_authorize_required
    def put_player_loadout(self, loadout: Mapping) -> Coroutine[Any, Any, None]:
        return self.http.put_player_loadout(loadout)

    @_authorize_required
    async def fetch_player_mmr(self, puuid: Optional[str] = None) -> MMR:
        data = await self.http.fetch_mmr(puuid)
        return MMR(client=self, data=data)

    async def fetch_match_history(
        self,
        puuid: Optional[str] = None,
        start_index: int = 0,
        end_index: int = 15,
        queue_id: Optional[str, QueueID] = QueueID.unrated,
        *,
        fetch_match_details: bool = True,
    ) -> Optional[MatchHistory]:
        data = await self.http.fetch_match_history(puuid, start_index, end_index, queue_id)
        history = MatchHistory(client=self, data=data) if data else None
        if fetch_match_details and history:
            await history.fetch_history()
        return history

    async def fetch_match_details(self, match_id: str) -> Optional[MatchDetails]:
        match_details = await self.http.fetch_match_details(match_id)
        return MatchDetails(client=self, data=match_details)

    # store endpoints

    @_authorize_required
    async def fetch_store_front(self) -> StoreFront:
        data = await self.http.store_fetch_storefront()
        return StoreFront(client=self, data=data)

    @_authorize_required
    async def fetch_wallet(self) -> Wallet:
        data = await self.http.store_fetch_wallet()
        return Wallet(client=self, data=data)
