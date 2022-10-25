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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from . import utils
from .assets import Assets
from .enums import ItemType, Locale, QueueID, try_enum
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
    ClientPlayer,
    Collection,
    CompetitiveTier,
    Content,
    ContentTier,
    Contract,
    Contracts,
    Currency,
    Entitlements,
    Event,
    Favorites,
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

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

# fmt: off
__all__ = (
    'Client',
)
# fmt: on

Coro = TypeVar('Coro', bound=Callable[..., Coroutine[Any, Any, Any]])

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
        self._with_assets: bool = kwargs.get('with_assets', False)
        self._reload_assets: bool = kwargs.get('reload_assets', False)

        self.loop: asyncio.AbstractEventLoop = _loop
        self.user: ClientPlayer = MISSING

        # config
        self._closed: bool = False
        self._ready: bool = False
        self._version: Version = MISSING
        self._season: Season = MISSING

        self._is_authorized: bool = False

        # http client
        self._http: HTTPClient = HTTPClient()

        # assets
        self.assets: Assets = Assets(client=self, auto_reload=self._reload_assets)

        # events
        self._listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}

    # events

    # source code from https://github.com/Rapptz/discord.py

    def _schedule_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task:
        wrapped = self._run_event(coro, event_name, *args, **kwargs)
        # Schedules the task
        return self.loop.create_task(wrapped, name=f'valorantx: {event_name}')

    async def _run_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:  # noqa
            try:
                await self.on_error(event_name, *args, **kwargs)
            except asyncio.CancelledError:
                pass

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        _log.debug('Dispatching event %s', event)
        method = 'on_' + event

        listeners = self._listeners.get(event)
        if listeners:
            removed = []
            for i, (future, condition) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue

                try:
                    result = condition(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(event)
            else:
                for idx in reversed(removed):
                    del listeners[idx]

        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_event(coro, method, *args, **kwargs)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        """|coro|

        The default error handler provided by the client.

        By default, this logs to the library logger however it could be
        overridden to have a different implementation.
        Check :func:`~valorant.on_error` for more details.
        """

        _log.exception('Ignoring exception in %s', event_method)

    def event(self, coro: Coro, /) -> Coro:
        """A decorator that registers an event to listen to.

        You can find more info about the events on the :ref:`documentation below <discord-api-events>`.

        The events must be a :ref:`coroutine <coroutine>`, if not, :exc:`TypeError` is raised.

        Example
        ---------

        .. code-block:: python3

            @client.event
            async def on_ready():
                print('Ready!')

        ``coro`` parameter is now positional-only.

        Raises
        --------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a coroutine function')

        setattr(self, coro.__name__, coro)
        _log.debug('%s has successfully been registered as an event', coro.__name__)
        return coro

    # end events

    async def __aenter__(self) -> Self:
        # do something
        loop = asyncio.get_running_loop()
        self.loop = loop
        if self.version is MISSING:
            self.version = await self.get_valorant_version()
        self.http._riot_client_version = self.version.riot_client_version

        if self._with_assets:
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
        riot_auth = await self.http.static_login(username.strip(), password.strip())
        payload = dict(
            puuid=riot_auth.user_id,
            username=riot_auth.name,
            tagline=riot_auth.tag,
            region=riot_auth.region,
        )
        self.user = ClientPlayer(client=self, data=payload)
        content = await self.fetch_content()
        for season in content.seasons:
            if season.is_active():
                self._season = self.get_season(uuid=season.id)
                break

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
    def season(self, value: Season) -> None:
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
        return Buddy(client=self, data=data) if data else self.get_buddy_level(*args, **kwargs)

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
        level = kwargs.get('level', True)
        data = self.assets.get_spray(*args, **kwargs)
        return Spray(client=self, data=data) if data else (self.get_spray_level(*args, **kwargs) if level else None)

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
        level = kwargs.get('level', True)
        chroma = kwargs.get('chroma', True)

        data = self.assets.get_skin(*args, **kwargs)
        return (
            Skin(client=self, data=data)
            if data
            else (
                self.get_skin_level(*args, **kwargs)
                if level
                else (self.get_skin_chroma(*args, **kwargs) if chroma else None)
            )
        )

    def get_skin_level(self, *args: Any, **kwargs: Any) -> Optional[SkinLevel]:
        """weapon_skins_levels, Get a weapon skin level by UUID."""
        data = self.assets.get_skin_level(*args, **kwargs)
        return SkinLevel(client=self, data=data) if data else None

    def get_skin_chroma(self, *args: Any, **kwargs: Any) -> Optional[SkinChroma]:
        """weapon_skins_chromas, Get a weapon skin chroma by UUID."""
        data = self.assets.get_skin_chroma(*args, **kwargs)
        return SkinChroma(client=self, data=data) if data else None

    # get all

    def get_all_agents(self) -> Iterator[Agent]:
        data = self.assets.get_asset('agents')
        for item in data.values():
            yield Agent(client=self, data=item)

    def get_all_bundles(self) -> Iterator[Bundle]:
        data = self.assets.get_asset('bundles')
        for item in data.values():
            yield Bundle(client=self, data=item)

    def get_all_buddies(self) -> Iterator[Buddy]:
        data = self.assets.get_asset('buddies')
        for item in data.values():
            yield Buddy(client=self, data=item)

    def get_all_buddy_levels(self) -> Iterator[BuddyLevel]:
        data = self.assets.get_asset('buddies_levels')
        for item in data.values():
            yield BuddyLevel(client=self, data=item)

    def get_all_player_titles(self) -> Iterator[PlayerTitle]:
        data = self.assets.get_asset('player_titles')
        for item in data.values():
            yield PlayerTitle(client=self, data=item)

    def get_all_player_cards(self) -> Iterator[PlayerCard]:
        data = self.assets.get_asset('player_cards')
        for item in data.values():
            yield PlayerCard(client=self, data=item)

    def get_all_skins(self) -> Iterator[Skin]:
        data = self.assets.get_asset('weapon_skins')
        for item in data.values():
            yield Skin(client=self, data=item)

    def get_all_skin_levels(self) -> Iterator[SkinLevel]:
        data = self.assets.get_asset('weapon_skins_levels')
        for item in data.values():
            yield SkinLevel(client=self, data=item)

    def get_all_skin_chromas(self) -> Iterator[SkinChroma]:
        data = self.assets.get_asset('weapon_skins_chromas')
        for item in data.values():
            yield SkinChroma(client=self, data=item)

    def get_all_sprays(self) -> Iterator[Spray]:
        data = self.assets.get_asset('sprays')
        for item in data.values():
            yield Spray(client=self, data=item)

    def get_all_spray_levels(self) -> Iterator[SprayLevel]:
        data = self.assets.get_asset('sprays_levels')
        for item in data.values():
            yield SprayLevel(client=self, data=item)

    def get_all_weapons(self) -> Iterator[Weapon]:
        data = self.assets.get_asset('weapons')
        for item in data.values():
            yield Weapon(client=self, data=item)

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
    async def fetch_loadout(self, *, with_xp: bool = True) -> Collection:

        data = await self.http.fetch_player_loadout()
        collection = Collection(client=self, data=data)
        if with_xp:
            account_xp = await self.fetch_account_xp()
            self.user.account_level = account_xp.level
            collection.identity.account_level = account_xp.level

        return collection

    @_authorize_required
    def put_loadout(self, loadout: Mapping) -> Any:  # TODO: loadout object
        return self.http.put_player_loadout(loadout)

    @_authorize_required
    async def fetch_mmr(self, puuid: Optional[str] = None) -> MMR:
        data = await self.http.fetch_mmr(puuid)
        return MMR(client=self, data=data)

    @_authorize_required
    async def fetch_match_history(
        self,
        puuid: Optional[str] = None,
        queue: Optional[str, QueueID] = QueueID.unrated,
        *,
        start: int = 0,
        end: int = 15,
        with_details: bool = True,
    ) -> Optional[MatchHistory]:
        data = await self.http.fetch_match_history(puuid, start, end, queue)
        history = MatchHistory(client=self, data=data) if data else None
        if with_details and history is not None:
            await history.fetch_details()
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
    async def fetch_order(self, order_id: str) -> Any:
        data = await self.http.store_fetch_order(order_id)
        # return Order(client=self, data=data)

    @_authorize_required
    async def fetch_entitlements(self, item_type: Optional[Union[str, ItemType]] = None) -> Any:
        data = await self.http.store_fetch_entitlements(item_type)
        return Entitlements(client=self, data=data)

    # favorite endpoints

    @_authorize_required
    async def fetch_favorites(self) -> Favorites:
        data = await self.http.favorites_fetch()
        return Favorites(client=self, data=data)

    @_authorize_required
    async def add_favorite(self, maybe_uuid: Union[str, Skin, PlayerCard, Spray]) -> Favorites:
        if isinstance(maybe_uuid, (Skin, PlayerCard, Spray)):
            maybe_uuid = maybe_uuid.uuid
        data = await self.http.favorite_post(maybe_uuid)
        return Favorites(client=self, data=data)

    @_authorize_required
    async def remove_favorite(self, maybe_uuid: Union[str, Skin, PlayerCard, Spray]) -> Favorites:
        if isinstance(maybe_uuid, (Skin, PlayerCard, Spray)):
            maybe_uuid = maybe_uuid.uuid
        data = await self.http.favorite_delete(maybe_uuid)
        return Favorites(client=self, data=data)
