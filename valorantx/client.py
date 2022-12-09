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
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from . import utils
from .assets import Assets
from .enums import ItemType, Locale, QueueType, try_enum
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
    NameService,
    Offers,
    Party,
    PartyPlayer,
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
    Tier,
    Version,
    Wallet,
    Weapon,
)

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

    # item = TypeVar('item', bound=ItemType)

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


def _authorize_required(func: Callable[..., Any]) -> Callable[[], Any]:
    def wrapper(self: Client = MISSING, *args: Any, **kwargs: Any) -> Any:
        if not self.is_authorized():
            client_func = f'Client.{func.__name__}'
            raise AuthRequired(f"{client_func!r} requires authorization")
        return func(self, *args, **kwargs)

    return wrapper


class Client:
    def __init__(self, *, locale: Union[Locale, str] = Locale.american_english, **kwargs: Any) -> None:

        self._locale: Locale = try_enum(Locale, locale) if isinstance(locale, str) else locale
        self._reload_assets: bool = kwargs.get('reload_assets', False)

        self.loop: asyncio.AbstractEventLoop = _loop
        self.user: ClientPlayer = MISSING

        # config
        self._closed: bool = False
        self._version: Version = MISSING
        self._season: Season = MISSING

        self._is_authorized: bool = False

        # http client
        self._http: HTTPClient = HTTPClient(self.loop)

        # assets
        self._assets: Assets = Assets(client=self)

        # events
        self._listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}

        self._ready: asyncio.Event = MISSING

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
        # TODO: docs
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
        self.http.loop = loop
        self._ready = asyncio.Event()
        await self.setup()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if not self.is_closed():
            await self.close()

    async def setup(self, *, reload: bool = False) -> None:

        _log.debug('Setting up client')

        if self.version is MISSING:
            self.version = await self.fetch_version()

        self.http._riot_client_version = self.version.riot_client_version

        await self._assets.fetch_assets(reload=reload, version=self.version)

        self._ready.set()

        _log.debug('Client setup complete')

    def is_ready(self) -> bool:
        """:class:`bool`: Specifies if the client's internal cache is ready for use."""
        return self._ready is not MISSING and self._ready.is_set()

    async def wait_until_ready(self) -> None:
        """|coro|
        Waits until the client's internal cache is all ready.
        .. warning::
            Calling this inside :meth:`setup_hook` can lead to a deadlock.
        """
        if self._ready is not MISSING:
            await self._ready.wait()
        else:
            raise RuntimeError(
                'Client has not been properly initialised. '
                'Please use the login method or asynchronous context manager before calling this method'
            )

    async def authorize(self, username: Optional[str], password: Optional[str]) -> None:
        """|coro|

        Authorize the client with the given username and password.

        Parameters
        -----------
        username: Optional[:class:`str`]
            The username of the account to authorize.
        password: Optional[:class:`str`]
            The password of the account to authorize.
        """

        if username is None or password is None:
            raise ValueError('Username or password cannot be None')

        self._is_authorized = True
        riot_auth = await self.http.static_login(username.strip(), password.strip())
        payload = dict(
            puuid=riot_auth.user_id,
            username=riot_auth.name,
            tagline=riot_auth.tag,
            region=riot_auth.region,
        )
        self.user = ClientPlayer(client=self, data=payload)
        if self.is_ready():
            content = await self.fetch_content()
            for season in reversed(content.get_seasons()):
                if season.is_active():
                    get_season = self.get_season(uuid=season.id)
                    if get_season is not None:
                        self.season = get_season
                        break

    async def authorize_from_data(self, data: Dict[str, Any]) -> None:
        self._is_authorized = True
        riot_auth = await self.http.token_login(data)
        payload = dict(
            puuid=riot_auth.user_id,
            username=riot_auth.name,
            tagline=riot_auth.tag,
            region=riot_auth.region,
        )
        self.user = ClientPlayer(client=self, data=payload)
        if self.is_ready():
            content = await self.fetch_content()
            for season in content.get_seasons():
                if season.is_active():
                    get_season = self.get_season(uuid=season.id)
                    if get_season is not None:
                        self.season = get_season
                        break

    def is_authorized(self) -> bool:
        """:class:`bool`: Whether the client is authorized."""
        return self._is_authorized

    # def run(self, username: Optional[str], password: Optional[str]) -> None:
    #     async def runner():
    #         async with self:
    #             await self.authorize(username, password)
    #
    #     try:
    #         asyncio.run(runner())
    #     except KeyboardInterrupt:
    #         # nothing to do here
    #         # `asyncio.run` handles the loop cleanup
    #         # and `self.start` closes all sockets and the HTTPClient instance.
    #         return

    def clear(self) -> None:
        """Clears the internal cache."""
        self._closed = False
        self._ready.clear()
        self._assets.clear()
        self._http.clear()

    async def close(self) -> None:
        """|coro|

        Closes the client session and logs out.
        """

        if self._closed:
            return
        self._closed = True
        await self._http.close()

    def is_closed(self) -> bool:
        """:class:`bool`: Indicates if the client is closed."""
        return self._closed

    @property
    def http(self) -> HTTPClient:
        """:class:`HTTPClient`: The HTTP client associated with this client."""
        return self._http

    @http.setter
    def http(self, http: HTTPClient) -> None:
        self._http = http

    @property
    def locale(self) -> Locale:
        """:class:`Locale`: The locale of the client."""
        return self._locale

    @locale.setter
    def locale(self, locale: Union[str, Locale]) -> None:
        self._locale = try_enum(Locale, locale) if isinstance(locale, str) else locale

    @property
    def version(self) -> Version:
        """:class:`Version`: The version of the client."""
        return self._version

    @version.setter
    def version(self, value: Version) -> None:
        if not isinstance(value, Version):
            raise TypeError(f"Expected Version, got {type(value).__name__}")
        self._version = value

    @property
    def season(self) -> Optional[Season]:
        """:class:`Season`: The season of the client."""
        return self._season

    @season.setter
    def season(self, value: Season) -> None:
        if not isinstance(value, Season):
            raise TypeError(f"Expected Season, got {type(value).__name__}")
        self._season = value

    # assets

    def fetch_assets(self, force: bool = False, reload: bool = False) -> Coroutine[Any, Any, None]:
        """:class:`coroutine`: Fetches the assets of the client."""
        return self._assets.fetch_assets(force=force, with_price=self._is_authorized, reload=reload)

    def reload_assets(self, with_price: bool = False) -> None:
        """Reloads the assets of the client."""
        self._assets.reload(with_price=with_price)

    def get_agent(self, *args: Any, **kwargs: Any) -> Optional[Agent]:
        """:class:`Optional[Agent]`: Gets an agent from the assets."""
        data = self._assets.get_agent(*args, **kwargs)
        return Agent(client=self, data=data) if data else None

    def get_buddy(self, *args: Any, **kwargs: Any) -> Optional[Union[Buddy, BuddyLevel]]:
        """:class:`Optional[Union[Buddy, BuddyLevel]]`: Gets a buddy from the assets."""
        data = self._assets.get_buddy(*args, **kwargs)
        return Buddy(client=self, data=data) if data else self.get_buddy_level(*args, **kwargs)

    def get_buddy_level(self, *args: Any, **kwargs: Any) -> Optional[BuddyLevel]:
        """:class:`Optional[BuddyLevel]`: Gets a buddy level from the assets."""
        data = self._assets.get_buddy_level(*args, **kwargs)
        return BuddyLevel(client=self, data=data) if data else None

    def get_bundle(self, *args: Any, **kwargs: Any) -> Optional[Bundle]:
        """:class:`Optional[Bundle]`: Gets a bundle from the assets."""
        data = self._assets.get_bundle(*args, **kwargs)
        return Bundle(client=self, data=data) if data else None

    def get_ceremony(self, *args: Any, **kwargs: Any) -> Optional[Ceremony]:
        """:class:`Optional[Ceremony]`: Gets a ceremony from the assets."""
        data = self._assets.get_ceremony(*args, **kwargs)
        return Ceremony(client=self, data=data) if data else None

    def get_competitive_tier(self, *args: Any, **kwargs: Any) -> Optional[CompetitiveTier]:
        """:class:`Optional[CompetitiveTier]`: Gets a competitive tier from the assets."""
        data = self._assets.get_competitive_tier(*args, **kwargs)
        return CompetitiveTier(client=self, data=data) if data else None

    def get_content_tier(self, *args: Any, **kwargs: Any) -> Optional[ContentTier]:
        """:class:`Optional[ContentTier]`: Gets a content tier from the assets."""
        data = self._assets.get_content_tier(*args, **kwargs)
        return ContentTier(client=self, data=data) if data else None

    def get_contract(self, *args: Any, **kwargs: Any) -> Optional[Contract]:
        """:class:`Optional[Contract]`: Gets a contract from the assets."""
        data = self._assets.get_contract(*args, **kwargs)
        return Contract(client=self, data=data) if data else None

    def get_currency(self, *args: Any, **kwargs: Any) -> Optional[Currency]:
        """:class:`Optional[Currency]`: Gets a currency from the assets."""
        data = self._assets.get_currency(*args, **kwargs)
        return Currency(client=self, data=data) if data else None

    def get_event(self, *args: Any, **kwargs: Any) -> Optional[Event]:
        """:class:`Optional[Event]`: Gets an event from the assets."""
        data = self._assets.get_event(*args, **kwargs)
        return Event(client=self, data=data) if data else None

    def get_game_mode(self, *args: Any, **kwargs: Any) -> Optional[GameMode]:
        """:class:`Optional[GameMode]`: Gets a game mode from the assets."""
        data = self._assets.get_game_mode(*args, **kwargs)
        return GameMode(client=self, data=data) if data else None

    def get_game_mode_equippable(self, *args: Any, **kwargs: Any) -> Optional[GameModeEquippable]:
        """:class:`Optional[GameModeEquippable]`: Gets a game mode equippable from the assets."""
        data = self._assets.get_game_mode_equippable(*args, **kwargs)
        return GameModeEquippable(client=self, data=data) if data else None

    def get_gear(self, *args: Any, **kwargs: Any) -> Optional[Gear]:
        """:class:`Optional[Gear]`: Gets a gear from the assets."""
        data = self._assets.get_gear(*args, **kwargs)
        return Gear(client=self, data=data) if data else None

    def get_level_border(self, *args: Any, **kwargs: Any) -> Optional[LevelBorder]:
        """:class:`Optional[LevelBorder]`: Gets a level border from the assets."""
        data = self._assets.get_level_border(*args, **kwargs)
        return LevelBorder(client=self, data=data) if data else None

    def get_map(self, *args: Any, **kwargs: Any) -> Optional[Map]:
        """:class:`Optional[Map]`: Gets a map from the assets."""
        data = self._assets.get_map(*args, **kwargs)
        return Map(client=self, data=data) if data else None

    def get_mission(self, *args: Any, **kwargs: Any) -> Optional[Mission]:
        """:class:`Optional[Mission]`: Gets a mission from the assets."""
        data = self._assets.get_mission(*args, **kwargs)
        return Mission(client=self, data=data) if data else None

    def get_player_card(self, *args: Any, **kwargs: Any) -> Optional[PlayerCard]:
        """:class:`Optional[PlayerCard]`: Gets a player card from the assets."""
        data = self._assets.get_player_card(*args, **kwargs)
        return PlayerCard(client=self, data=data) if data else None

    def get_player_title(self, *args: Any, **kwargs: Any) -> Optional[PlayerTitle]:
        """:class:`Optional[PlayerTitle]`: Gets a player title from the assets."""
        data = self._assets.get_player_title(*args, **kwargs)
        return PlayerTitle(client=self, data=data) if data else None

    def get_season(self, *args: Any, **kwargs: Any) -> Optional[Season]:
        """:class:`Optional[Season]`: Gets a season from the assets."""
        data = self._assets.get_season(*args, **kwargs)
        return Season(client=self, data=data) if data else None

    def get_season_competitive(self, *args: Any, **kwargs: Any) -> Optional[SeasonCompetitive]:
        """:class:`Optional[SeasonCompetitive]`: Gets a season competitive from the assets."""
        data = self._assets.get_season_competitive(*args, **kwargs)
        return SeasonCompetitive(client=self, data=data) if data else None

    @overload
    def get_spray(self, uuid: str, level=False) -> Optional[Spray]:
        ...

    @overload
    def get_spray(self, uuid: str, level=True) -> Optional[Union[Spray, SprayLevel]]:
        ...

    def get_spray(self, *args: Any, **kwargs: Any) -> Optional[Union[Spray, SprayLevel]]:
        """:class:`Optional[Union[Spray, SprayLevel]]`: Gets a spray from the assets."""
        level = kwargs.get('level', True)
        data = self._assets.get_spray(*args, **kwargs)
        return Spray(client=self, data=data) if data else (self.get_spray_level(*args, **kwargs) if level else None)

    def get_spray_level(self, *args: Any, **kwargs: Any) -> Optional[SprayLevel]:
        """:class:`Optional[SprayLevel]`: Gets a spray level from the assets."""
        data = self._assets.get_spray_level(*args, **kwargs)
        return SprayLevel(client=self, data=data) if data else None

    def get_theme(self, *args: Any, **kwargs: Any) -> Optional[Theme]:
        """:class:`Optional[Theme]`: Gets a theme from the assets."""
        data = self._assets.get_theme(*args, **kwargs)
        return Theme(client=self, data=data) if data else None

    def get_weapon(self, *args: Any, **kwargs: Any) -> Optional[Weapon]:
        """Optional[:class:`Weapon`]: Gets a weapon from the assets."""
        data = self._assets.get_weapon(*args, **kwargs)
        return Weapon(client=self, data=data) if data else None

    @overload
    def get_skin(self, uuid: str, level=False) -> Optional[Union[Skin, SkinChroma]]:
        ...

    @overload
    def get_skin(self, uuid: str, chroma=False) -> Optional[Union[Skin, SkinLevel]]:
        ...

    @overload
    def get_skin(self, uuid: str, level=False, chroma=False) -> Optional[Skin]:
        ...

    def get_skin(self, *args: Any, **kwargs: Any) -> Optional[Union[Skin, SkinLevel, SkinChroma]]:
        """Optional[:class:`Union[Skin, SkinLevel, SkinChroma]`]: Gets a skin from the assets."""
        level = kwargs.get('level', False)
        chroma = kwargs.get('chroma', False)

        data = self._assets.get_skin(*args, **kwargs)
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
        """Optional[:class:`SkinLevel`]: Gets a skin level from the assets."""
        data = self._assets.get_skin_level(*args, **kwargs)
        return SkinLevel(client=self, data=data) if data else None

    def get_skin_chroma(self, *args: Any, **kwargs: Any) -> Optional[SkinChroma]:
        """Optional[:class:`SkinChroma`]: Gets a skin chroma from the assets."""
        data = self._assets.get_skin_chroma(*args, **kwargs)
        return SkinChroma(client=self, data=data) if data else None

    def get_tier(self, tier_number: int, season: Optional[Season] = None) -> Optional[Tier]:
        if season is None:
            season = self.season
        ss_com_all = self.get_all_season_competitive()
        for ss_com in ss_com_all:
            if ss_com.season == season:
                ss_com_tiers = ss_com.competitive_tiers
                if ss_com_tiers is None:
                    return None
                for tier in ss_com_tiers.tiers:
                    if tier.tier == tier_number:
                        return tier

    # get all

    def get_all_agents(self) -> Iterator[Agent]:
        """Gets all agents from the assets.

        Yields
        -------
        :class:`Agent`
            The agent.
        """
        data = self._assets.get_asset('agents')
        if data is None:
            return
        for item in data.values():
            yield Agent(client=self, data=item)

    def get_all_buddies(self) -> Iterator[Buddy]:
        """Gets all buddies from the assets.

        Yields
        -------
        :class:`Buddy`
            The buddy.
        """
        data = self._assets.get_asset('buddies')
        if data is None:
            return
        for item in data.values():
            yield Buddy(client=self, data=item)

    def get_all_buddy_levels(self) -> Iterator[BuddyLevel]:
        """Gets all buddy levels from the assets.

        Yields
        -------
        :class:`BuddyLevel`
            The buddy level.
        """
        data = self._assets.get_asset('buddies_levels')
        if data is None:
            return
        for item in data.values():
            yield BuddyLevel(client=self, data=item)

    def get_all_bundles(self) -> Iterator[Bundle]:
        """Gets all bundles from the assets.

        Yields
        -------
        :class:`Bundle`
            The bundle.
        """
        data = self._assets.get_asset('bundles')
        if data is None:
            return
        for item in data.values():
            yield Bundle(client=self, data=item)

    def get_all_player_titles(self) -> Iterator[PlayerTitle]:
        """Gets all player titles from the assets.

        Yields
        -------
        :class:`PlayerTitle`
            The player title.
        """
        data = self._assets.get_asset('player_titles')
        if data is None:
            return
        for item in data.values():
            yield PlayerTitle(client=self, data=item)

    def get_all_player_cards(self) -> Iterator[PlayerCard]:
        """Gets all player cards from the assets.

        Yields
        -------
        :class:`PlayerCard`
            The player card.
        """
        data = self._assets.get_asset('player_cards')
        if data is None:
            return
        for item in data.values():
            yield PlayerCard(client=self, data=item)

    def get_all_skins(self) -> Iterator[Skin]:
        """Gets all skins from the assets.

        Yields
        -------
        :class:`Skin`
            The skin.
        """
        data = self._assets.get_asset('weapon_skins')
        if data is None:
            return
        for item in data.values():
            yield Skin(client=self, data=item)

    def get_all_skin_levels(self) -> Iterator[SkinLevel]:
        """Gets all skin levels from the assets.

        Yields
        -------
        :class:`SkinLevel`
            The skin level.
        """
        data = self._assets.get_asset('weapon_skins_levels')
        if data is None:
            return
        for item in data.values():
            yield SkinLevel(client=self, data=item)

    def get_all_skin_chromas(self) -> Iterator[SkinChroma]:
        """Gets all skin chromas from the assets.

        Yields
        -------
        :class:`SkinChroma`
            The skin chroma.
        """
        data = self._assets.get_asset('weapon_skins_chromas')
        if data is None:
            return
        for item in data.values():
            yield SkinChroma(client=self, data=item)

    def get_all_sprays(self) -> Iterator[Spray]:
        """Gets all sprays from the assets.

        Yields
        -------
        :class:`Spray`
            The spray.
        """
        data = self._assets.get_asset('sprays')
        if data is None:
            return
        for item in data.values():
            yield Spray(client=self, data=item)

    def get_all_spray_levels(self) -> Iterator[SprayLevel]:
        """Gets all spray levels from the assets.

        Yields
        -------
        :class:`SprayLevel`
            The spray level.
        """
        data = self._assets.get_asset('sprays_levels')
        if data is None:
            return
        for item in data.values():
            yield SprayLevel(client=self, data=item)

    def get_all_weapons(self) -> Iterator[Weapon]:
        """Gets all weapons from the assets.

        Yields
        -------
        :class:`Weapon`
            The weapon.
        """
        data = self._assets.get_asset('weapons')
        if data is None:
            return
        for item in data.values():
            yield Weapon(client=self, data=item)

    def get_all_season_competitive(self) -> Iterator[SeasonCompetitive]:
        """Gets all seasons from the assets.

        Yields
        -------
        :class:`SeasonCompetitive`
            The season.
        """
        data = self._assets.get_asset('seasons_competitive')
        if data is None:
            return
        for item in data.values():
            yield SeasonCompetitive(client=self, data=item)

    def get_all_events(self) -> Iterator[Event]:
        """Gets all events from the assets.

        Yields
        -------
        :class:`Event`
            The event.
        """
        data = self._assets.get_asset('events')
        if data is None:
            return
        for item in data.values():
            yield Event(client=self, data=item)

    def get_all_seasons(self) -> Iterator[Season]:
        """Gets all seasons from the assets.

        Yields
        -------
        :class:`Season`
            The season.
        """
        data = self._assets.get_asset('seasons')
        if data is None:
            return
        for item in data.values():
            yield Season(client=self, data=item)

    def get_item_price(
        self, item: Union[str, Skin, SkinChroma, SkinLevel, PlayerCard, Buddy, BuddyLevel, Spray, SprayLevel]
    ) -> int:
        """Gets the price of an item

        Parameters
        ----------
        item: :class:`str`
            The uuid of the item

        Returns
        -------
        :class:`int`
            The price of the item
        """

        uuid = '' if not isinstance(item, str) else item

        if isinstance(item, Skin):
            skin_lv1 = item.get_skin_level(level=1)
            if skin_lv1 is not None:
                uuid = skin_lv1.uuid
        elif isinstance(item, SkinChroma):
            skin = item.get_skin()
            if skin is not None:
                skin_lv1 = skin.get_skin_level(level=1)
                if skin_lv1 is not None:
                    uuid = skin_lv1.uuid
        elif isinstance(item, Buddy):
            buddy_lv1 = item.get_buddy_level(level=1)
            if buddy_lv1 is not None:
                uuid = buddy_lv1.uuid
        elif isinstance(item, SprayLevel):
            spray = item.get_base_spray()
            if spray is not None:
                uuid = spray.uuid
        elif isinstance(item, (SkinLevel, PlayerCard, Spray, BuddyLevel)):
            uuid = item.uuid

        return self._assets.get_item_price(uuid)

    @staticmethod
    async def http_fetch_version(http: Optional[HTTPClient] = None) -> Version:
        """|coro|

        Fetches the current valorant version directly from the API.

        Returns
        -------
        :class:`Version`
            The current version of Valorant.
        """
        if http is None:
            http = HTTPClient()
        data = await http.asset_valorant_version()
        return Version(data=data)

    async def fetch_version(self) -> Version:
        """|coro|

        Fetches the current valorant version.

        Returns
        -------
        :class:`Version`
            The current version of Valorant.
        """
        return await self.http_fetch_version(self.http)

    # patch notes

    async def fetch_patch_notes(self, locale: Union[str, Locale] = Locale.american_english) -> PatchNotes:
        """|coro|

        Fetches the patch notes for the current version of Valorant.

        Parameters
        ----------
        locale: Union[:class:`str`, :class:`Locale`]
            The locale to fetch the patch notes in.

        Returns
        -------
        :class:`PatchNotes`
            The patch notes for the current version of Valorant.
        """

        if isinstance(locale, str):
            locale = try_enum(Locale, str(locale))

        # endpoint is not available for simplified chinese
        if locale is Locale.chinese_simplified:
            locale = Locale.chinese_traditional
        data = await self.http.fetch_patch_notes(locale)

        return PatchNotes(client=self, data=data, locale=locale)

    # player endpoints

    async def fetch_name_by_puuid(self, puuid: Optional[Union[List[str], str]] = None) -> List[NameService]:
        """|coro|

        Fetches the name history of a player by their puuid.

        Parameters
        ----------
        puuid: Optional[Union[:class:`str`, :class:`List[:class:`str`]]]
            The puuid of the player.

        Returns
        -------
        :class:`List[:class:`NameService`]`
            The name history of the player.
        """
        data = await self.http.fetch_name_by_puuid(puuid)
        return [NameService(data=name) for name in data]

    # PVP endpoints

    @_authorize_required
    async def fetch_content(self) -> Content:
        """|coro|

        Fetches the content for the current version of Valorant.

        Returns
        -------
        :class:`Content`
            The content for the current version of Valorant.
        """
        data = await self.http.fetch_content()
        return Content(client=self, data=data)

    @_authorize_required
    async def fetch_account_xp(self) -> AccountXP:
        """|coro|

        Fetches the account XP for the current user.

        Returns
        -------
        :class:`AccountXP`
            The account XP for the current user.
        """
        data = await self.http.fetch_account_xp()
        return AccountXP(client=self, data=data)

    @_authorize_required
    async def fetch_collection(self, *, with_xp: bool = True, with_favorite: bool = True) -> Collection:
        """|coro|

        Fetches the collection for the current user.

        Parameters
        ----------
        with_xp: :class:`bool`
            Whether to include the XP for each item in the loadout.
        with_favorite: :class:`bool`
            Whether to include the favorite status for each item in the loadout.

        Returns
        -------
        :class:`Collection`
            The collection for the current user.
        """
        data = await self.http.fetch_player_loadout()
        collection = Collection(client=self, data=data)

        if with_xp:
            await collection.fetch_account_xp()

        if with_favorite:
            await collection.fetch_favorites()

        return collection

    @_authorize_required
    async def put_loadout(self, loadout: Mapping[str, Any]) -> None:  # TODO: loadout object
        """|coro|

        Puts the loadout for the current user.

        Parameters
        ----------
        loadout: :class:`Mapping`
            The loadout to put.

        Returns
        -------
        :class:`Any`
            The response from the API.
        """
        # await self.http.put_player_loadout(loadout)
        pass

    @_authorize_required
    async def fetch_mmr(self, puuid: Optional[str] = None) -> MMR:
        """|coro|

        Fetches the MMR for the current user or a given user.

        Parameters
        ----------
        puuid: Optional[:class:`str`]
            The puuid of the user to fetch the MMR for.

        Returns
        -------
        :class:`MMR`
            The MMR for the current user or a given user.
        """
        data = await self.http.fetch_mmr(puuid)
        return MMR(client=self, data=data)

    @_authorize_required
    async def fetch_match_history(
        self,
        puuid: Optional[str] = None,
        queue: Optional[Union[str, QueueType]] = None,
        *,
        start: int = 0,
        end: int = 15,
        with_details: bool = True,
    ) -> Optional[MatchHistory]:
        """|coro|

        Fetches the match history for the current user or a given user.

        Parameters
        ----------
        puuid: Optional[:class:`str`]
            The puuid of the user to fetch the match history for.
        queue: Optional[Union[:class:`str`, :class:`QueueType`]]
            The queue to fetch the match history for.
        start: :class:`int`
            The start index of the match history.
        end: :class:`int`
            The end index of the match history.
        with_details: :class:`bool`
            Whether to include the details for each match in the match history.

        Returns
        -------
        Optional[:class:`MatchHistory`]
            The match history for the current user or a given user.
        """
        data = await self.http.fetch_match_history(puuid, start, end, queue)
        history = MatchHistory(client=self, data=data) if data else None
        if with_details and history is not None:
            await history.fetch_details()
        return history

    @_authorize_required
    async def fetch_match_details(self, match_id: str) -> Optional[MatchDetails]:
        """|coro|

        Fetches the match details for a given match.

        Parameters
        ----------
        match_id: :class:`str`
            The match ID to fetch the match details for.

        Returns
        -------
        Optional[:class:`MatchDetails`]
            The match details for a given match.
        """
        match_details = await self.http.fetch_match_details(match_id)
        return MatchDetails(client=self, data=match_details)

    # contract endpoints

    @_authorize_required
    async def fetch_contracts(self) -> Contracts:
        """|coro|

        Fetches the contracts for the current user.

        Returns
        -------
        :class:`Contracts`
            The contracts for the current user.
        """
        data = await self.http.contracts_fetch()
        return Contracts(client=self, data=data)

    # store endpoints

    @_authorize_required
    async def fetch_offers(self) -> Offers:
        """|coro|

        Fetches the offers for the current user.

        Returns
        -------
        :class:`Offers`
            The offers for the current user.
        """
        data = await self.http.store_fetch_offers()
        return Offers(data=data)

    @_authorize_required
    async def fetch_store_front(self) -> StoreFront:
        """|coro|

        Fetches the storefront for the current user.

        Returns
        -------
        :class:`StoreFront`
            The storefront for the current user.
        """
        data = await self.http.store_fetch_storefront()
        return StoreFront(client=self, data=data)

    @_authorize_required
    async def fetch_wallet(self) -> Wallet:
        """|coro|

        Fetches the wallet for the current user.

        Returns
        -------
        :class:`Wallet`
            The wallet for the current user.
        """
        data = await self.http.store_fetch_wallet()
        return Wallet(client=self, data=data)

    @_authorize_required
    async def fetch_order(self, order_id: str) -> Any:
        """|coro|

        Fetches the order for the current user.

        Parameters
        ----------
        order_id: :class:`str`
            The order ID to fetch the order for.

        Returns
        -------
        :class:`Any`
            The order for the current user.
        """
        data = await self.http.store_fetch_order(order_id)
        # return Order(client=self, data=data)

    @_authorize_required
    async def fetch_entitlements(self, item_type: Optional[Union[str, ItemType]] = None) -> Entitlements:
        """|coro|

        Fetches the entitlements for the current user.

        Parameters
        ----------
        item_type: Optional[Union[:class:`str`, :class:`ItemType`]]
            The item type to fetch the entitlements for.


        Returns
        -------
        :class:`Entitlements`
            The entitlements for the current user.
        """
        data = await self.http.store_fetch_entitlements(item_type)
        return Entitlements(client=self, data=data)

    # favorite endpoints

    @_authorize_required
    async def fetch_favorites(self) -> Favorites:
        """|coro|

        Fetches the favorites items for the current user.

        Returns
        -------
        :class:`Favorites`
            The favorites items for the current user.
        """
        data = await self.http.favorites_fetch()
        return Favorites(client=self, data=data)

    @_authorize_required
    async def add_favorite(self, item: Union[str, Buddy, PlayerCard, Skin, Spray, LevelBorder]) -> Favorites:
        """|coro|

        Adds a favorite item for the current user.

        Parameters
        ----------
        item: Union[:class:`str`, :class:`Buddy`, :class:`PlayerCard`, :class:`Skin`, :class:`Spray`]
            The item to add as a favorite.

        Returns
        -------
        :class:`Favorites`
            The favorites items for the current user.
        """
        if isinstance(item, (Buddy, PlayerCard, Skin, Spray, LevelBorder)):
            uuid = item.uuid
        else:
            uuid = item if utils.is_uuid(item) else ''
        data = await self._http.favorite_post(uuid)
        return Favorites(client=self, data=data)

    @_authorize_required
    async def remove_favorite(self, item: Union[str, Buddy, PlayerCard, Skin, Spray, LevelBorder]) -> Favorites:
        """|coro|

        Removes a favorite item for the current user.

        Parameters
        ----------
        item: Union[:class:`str`, :class:`Buddy`, :class:`PlayerCard`, :class:`Skin`, :class:`Spray`, :class:`LevelBorder`]
            The item to remove as a favorite.

        Returns
        -------
        :class:`Favorites`
            The favorites items for the current user.
        """
        if isinstance(item, (Buddy, PlayerCard, Skin, Spray, LevelBorder)):
            uuid = item.uuid
        else:
            uuid = item if utils.is_uuid(item) else ''
        data = await self.http.favorite_delete(uuid)
        return Favorites(client=self, data=data)

    # party endpoint

    @_authorize_required
    async def fetch_party(self, party_id: Optional[Union[Party, str]] = None) -> Party:

        if party_id is None:
            party_id = await self.fetch_party_player()

        if isinstance(party_id, PartyPlayer):
            party_id = party_id.id

        data = await self.http.fetch_party(party_id=str(party_id))
        party = Party(client=self, data=data)
        await party.update_member_display_name()
        return party

    @_authorize_required
    async def fetch_party_player(self) -> PartyPlayer:
        data = await self.http.party_fetch_player()
        return PartyPlayer(client=self, data=data)

    @_authorize_required
    async def party_request_to_join(self, party_id: str) -> Any:
        return ...

    @_authorize_required
    async def party_leave_from_party(self, party_id: str) -> Any:
        return ...

    # pre game lobby endpoints

    @_authorize_required
    async def fetch_pregame_match(self, match: Optional[str] = None) -> Any:
        if match is None:
            match = await self.fetch_pregame_player()
        data = await self.http.pregame_fetch_match(match_id=match)
        ...

    @_authorize_required
    async def fetch_pregame_player(self) -> Any:
        data = await self.http.pregame_fetch_player()
        ...
