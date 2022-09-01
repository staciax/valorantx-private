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
from .enums import ItemType, Locale, QueueID, try_enum
from .errors import AuthRequired
from .http import HTTPClient
from .models import (
    MMR,
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
    Contracts,
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
    Offers,
    PatchNotes,
    PlayerCard,
    PlayerTitle,
    Season,
    SeasonCompetitive,
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
from .models.xp import AccountXP

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


class _LoopSentinel:
    __slots__ = ()

    def __getattr__(self, attr: str) -> None:
        msg = (
            'loop attribute cannot be accessed in non-async contexts. '
            'Consider using either an asynchronous main function and passing it to asyncio.run or '
        )
        raise AttributeError(msg)


_loop: Any = _LoopSentinel()
# source: discord.py
# link: https://github.com/Rapptz/discord.py/blob/9ea6ee8887b65f21ccc0bcf013786f4ea61ba608/discord/client.py#L111


def _authorize_required(func):
    def wrapper(self: Optional[Client] = MISSING, *args: Any, **kwargs: Any) -> Any:
        if not self.is_authorized():
            client_func = f'Client.{func.__name__}'
            raise AuthRequired(f"{client_func!r} requires authorization")
        return func(self, *args, **kwargs)

    return wrapper


class Client:
    def __init__(self, *, locale: Union[Locale, str] = Locale.american_english, **kwargs: Any) -> None:

        self._locale: Union[Locale, str] = locale
        self._auto_fetch_assets: bool = kwargs.get('auto_fetch_assets', False)
        self._auto_reload_assets: bool = kwargs.get('auto_reload_assets', False)

        self.loop: asyncio.AbstractEventLoop = _loop

        # config
        self._closed: bool = False
        self._ready: bool = False
        self._version: Version = MISSING
        self._season: Season = MISSING

        self._is_authorized: bool = False

        # http client
        self._http: HTTPClient = HTTPClient()

        # assets
        self.assets: Assets = Assets(client=self, auto_reload=self._auto_reload_assets)

    async def __aenter__(self) -> Self:
        # do something
        loop = asyncio.get_running_loop()
        self.loop = loop
        if self.version is MISSING:
            self.version = await self.get_valorant_version()

        if self._auto_fetch_assets:
            await self.assets.fetch_assets()

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

    def fetch_assets(
        self, force: bool = False, with_price: bool = False, *, reload: bool = True
    ) -> Coroutine[Any, Any, Any]:
        return self.assets.fetch_assets(force=force, with_price=with_price, reload_asset=reload)

    def reload_assets(self, with_price: bool = False) -> None:
        self.assets.reload_assets(with_price=with_price)

    def get_agent(self, *args: Any, **kwargs: Any) -> Optional[Agent]:
        """Get an agent by UUID or Display Name."""
        data = self.assets.get_agent(*args, **kwargs)
        return Agent(client=self, data=data) if data else None

    def get_buddy(self, *args: Any, **kwargs: Any) -> Optional[Union[Buddy, BuddyLevel]]:
        """Get a buddy by UUID or Display Name."""
        data = self.assets.get_buddy(*args, **kwargs)
        return Buddy(client=self, data=data) if data else self.get_buddy_level(**kwargs)

    def get_buddy_level(self, *args: Any, **kwargs: Any) -> Optional[BuddyLevel]:
        """Get a buddy level by UUID or Display Name."""
        data = self.assets.get_buddy_level(*args, **kwargs)
        return BuddyLevel(client=self, data=data) if data else None

    def get_bundle(self, *args: Any, **kwargs: Any) -> Optional[Bundle]:
        """Get a bundle by UUID or Display Name."""
        data = self.assets.get_bundle(*args, **kwargs)
        return Bundle(client=self, data=data) if data else None

    def get_ceremony(self, *args: Any, **kwargs: Any) -> Optional[Ceremony]:
        """Get a ceremony by UUID."""
        data = self.assets.get_ceremony(*args, **kwargs)
        return Ceremony(client=self, data=data) if data else None

    def get_competitive_tier(self, *args: Any, **kwargs: Any) -> Optional[CompetitiveTier]:
        """Get a competitive tier by UUID."""
        data = self.assets.get_competitive_tier(*args, **kwargs)
        return CompetitiveTier(client=self, data=data) if data else None

    def get_content_tier(self, *args: Any, **kwargs: Any) -> Optional[ContentTier]:
        """Get a content tier by UUID."""
        data = self.assets.get_content_tier(*args, **kwargs)
        return ContentTier(client=self, data=data) if data else None

    def get_contract(self, *args: Any, **kwargs: Any) -> Optional[Contract]:
        """Get a contract by UUID."""
        data = self.assets.get_contract(*args, **kwargs)
        return Contract(client=self, data=data) if data else None

    def get_currency(self, *args: Any, **kwargs: Any) -> Optional[Currency]:
        """Get a currency by UUID."""
        data = self.assets.get_currency(*args, **kwargs)
        return Currency(client=self, data=data) if data else None

    def get_event(self, *args: Any, **kwargs: Any) -> Optional[Event]:
        """Get an event by UUID."""
        data = self.assets.get_event(*args, **kwargs)
        return Event(client=self, data=data) if data else None

    def get_game_mode(self, *args: Any, **kwargs: Any) -> Optional[GameMode]:
        """Get a game mode by UUID."""
        data = self.assets.get_game_mode(*args, **kwargs)
        return GameMode(client=self, data=data) if data else None

    def get_game_mode_equippable(self, *args: Any, **kwargs: Any) -> Optional[GameModeEquippable]:
        """Get a game mode equippable by UUID."""
        data = self.assets.get_game_mode_equippable(*args, **kwargs)
        return GameModeEquippable(client=self, data=data) if data else None

    def get_gear(self, *args: Any, **kwargs: Any) -> Optional[Gear]:
        """Get a gear by UUID."""
        data = self.assets.get_gear(*args, **kwargs)
        return Gear(client=self, data=data) if data else None

    def get_level_border(self, *args: Any, **kwargs: Any) -> Optional[LevelBorder]:
        """Get a level border by UUID."""
        data = self.assets.get_level_border(*args, **kwargs)
        return LevelBorder(client=self, data=data) if data else None

    def get_map(self, *args: Any, **kwargs: Any) -> Optional[Map]:
        """Get a map by UUID."""
        data = self.assets.get_map(*args, **kwargs)
        return Map(client=self, data=data) if data else None

    def get_mission(self, *args: Any, **kwargs: Any) -> Optional[Mission]:
        """missions, Get a mission by UUID."""
        data = self.assets.get_mission(*args, **kwargs)
        return Mission(client=self, data=data) if data else None

    def get_player_card(self, *args: Any, **kwargs: Any) -> Optional[PlayerCard]:
        """player_cards, Get a player card by UUID."""
        data = self.assets.get_player_card(*args, **kwargs)
        return PlayerCard(client=self, data=data) if data else None

    def get_player_title(self, *args: Any, **kwargs: Any) -> Optional[PlayerTitle]:
        """player_titles, Get a player title by UUID."""
        data = self.assets.get_player_title(*args, **kwargs)
        return PlayerTitle(client=self, data=data) if data else None

    def get_season(self, *args: Any, **kwargs: Any) -> Optional[Season]:
        """seasons, Get a season by UUID."""
        data = self.assets.get_season(*args, **kwargs)
        return Season(client=self, data=data) if data else None

    def get_season_competitive(self, *args: Any, **kwargs: Any) -> Optional[SeasonCompetitive]:
        """seasons, Get a season competitive by UUID."""
        data = self.assets.get_season_competitive(*args, **kwargs)
        return SeasonCompetitive(client=self, data=data) if data else None

    def get_spray(self, *args: Any, **kwargs: Any) -> Optional[Union[Spray, SprayLevel]]:
        """Get a spray by UUID."""
        data = self.assets.get_spray(*args, **kwargs)
        return Spray(client=self, data=data) if data else self.get_spray_level(**kwargs)

    def get_spray_level(self, *args: Any, **kwargs: Any) -> Optional[SprayLevel]:
        """Get a spray level by UUID."""
        data = self.assets.get_spray_level(*args, **kwargs)
        return SprayLevel(client=self, data=data) if data else None

    def get_theme(self, *args: Any, **kwargs: Any) -> Optional[Theme]:
        """themes, Get a theme by UUID."""
        data = self.assets.get_theme(*args, **kwargs)
        return Theme(client=self, data=data) if data else None

    def get_weapon(self, *args: Any, **kwargs: Any) -> Optional[Weapon]:
        """weapons, Get a weapon by UUID."""
        data = self.assets.get_weapon(*args, **kwargs)
        return Weapon(client=self, data=data) if data else None

    def get_skin(self, *args: Any, **kwargs: Any) -> Optional[Union[Skin, SkinLevel, SkinChroma]]:
        """weapon_skins, Get a weapon skin by UUID."""
        data = self.assets.get_skin(*args, **kwargs)
        return Skin(client=self, data=data) if data else self.get_skin_level(**kwargs) or self.get_skin_chroma(**kwargs)

    def get_skin_level(self, *args: Any, **kwargs: Any) -> Optional[SkinLevel]:
        """weapon_skins_levels, Get a weapon skin level by UUID."""
        data = self.assets.get_skin_level(*args, **kwargs)
        return SkinLevel(client=self, data=data) if data else None

    def get_skin_chroma(self, *args: Any, **kwargs: Any) -> Optional[SkinChroma]:
        """weapon_skins_chromas, Get a weapon skin chroma by UUID."""
        data = self.assets.get_skin_chroma(*args, **kwargs)
        return SkinChroma(client=self, data=data) if data else None

    def get_all_bundles(self) -> Iterator[Bundle]:
        data = self.assets.get_asset('bundles')
        for item in data.values():
            yield Bundle(client=self, data=item)

    def get_item_price(self, uuid: str) -> int:
        """Get the price of an item by UUID."""
        return self.assets.get_item_price(uuid)

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
        if fetch_account_xp:
            account_xp = await self.fetch_account_xp()
            # self.user._account_level = account_xp.level  # TODO: add to user class
        data = await self.http.fetch_player_loadout()
        return Collection(client=self, data=data)

    @_authorize_required
    def put_player_loadout(self, loadout: Mapping) -> Any:
        return self.http.put_player_loadout(loadout)

    @_authorize_required
    async def fetch_player_mmr(self, puuid: Optional[str] = None) -> MMR:
        data = await self.http.fetch_mmr(puuid)
        return MMR(client=self, data=data)

    @_authorize_required
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

    @_authorize_required
    async def fetch_match_details(self, match_id: str) -> Optional[MatchDetails]:
        match_details = await self.http.fetch_match_details(match_id)
        return MatchDetails(client=self, data=match_details)

    # contract endpoints

    @_authorize_required
    async def fetch_contracts(self) -> Contracts:
        data = await self.http.contracts_fetch()
        return Contracts(client=self, data=data)

    # store endpoints

    @_authorize_required
    async def fetch_offers(self) -> Offers:
        data = await self.http.store_fetch_offers()
        return Offers(data=data)

    @_authorize_required
    async def fetch_store_front(self) -> StoreFront:
        data = await self.http.store_fetch_storefront()
        return StoreFront(client=self, data=data)

    @_authorize_required
    async def fetch_wallet(self) -> Wallet:
        data = await self.http.store_fetch_wallet()
        return Wallet(client=self, data=data)

    @_authorize_required
    def fetch_order(self, order_id: str) -> Any:
        data = self.http.store_fetch_order(order_id)
        # return Order(client=self, data=data)

    @_authorize_required
    def fetch_entitlements(self, item_type: Union[str, ItemType] = ItemType.skin) -> Any:
        data = self.http.store_fetch_entitlements(item_type)
        # return Entitlements(client=self, data=data)
