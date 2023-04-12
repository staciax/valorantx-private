from __future__ import annotations

import asyncio
import logging
from typing import (  # Dict,; Iterator,; List,; Mapping,; overload,
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Optional,
    Type,
    TypeVar,
    Union,
)

from . import utils

# from .assets import Assets
from .enums import Locale, try_enum  # ItemType, QueueType, SeasonType,
from .errors import AuthRequired
from .http import HTTPClient
from .models import ClientUser, Entitlements, Offers, StoreFront, Wallet
from .valorant_api_client import Client as ValorantAPIClient

#     MMR,
#     AccountXP,
#     Agent,
#     Buddy,
#     BuddyLevel,
#     Bundle,
#     Ceremony,
#     ClientPlayer,
#     Collection,
#     CompetitiveTier,
#     Content,
#     ContentTier,
#     Contract,
#     Contracts,
#     Currency,
#     Entitlements,
#     Event,
#     Favorites,
#     GameMode,
#     GameModeEquippable,
#     Gear,
#     LevelBorder,
#     Map,
#     MatchDetails,
#     MatchHistory,
#     Mission,
#     NameService,
#     Offers,
#     Party,
#     PartyPlayer,
#     PatchNotes,
#     PlayerCard,
#     PlayerTitle,
#     Season,
#     SeasonCompetitive,
#     Skin,
#     SkinChroma,
#     SkinLevel,
#     Spray,
#     SprayLevel,
#     StoreFront,
#     Theme,
#     Tier,
#     Version,
#     Wallet,
#     Weapon,
# )

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import ParamSpec, Self

    from .valorant_api.models.version import Version as ValorantAPIVersion

    P = ParamSpec('P')

# fmt: off
__all__ = (
    'Client',
)
# fmt: on

T = TypeVar('T')
Coro = TypeVar('Coro', bound=Callable[..., Coroutine[Any, Any, Any]])

_log = logging.getLogger(__name__)

MISSING: Any = utils.MISSING


# -- from discord.py
# link: https://github.com/Rapptz/discord.py/blob/9ea6ee8887b65f21ccc0bcf013786f4ea61ba608/discord/client.py#L111
class _LoopSentinel:
    __slots__ = ()

    def __getattr__(self, attr: str) -> None:
        msg = (
            'loop attribute cannot be accessed in non-async contexts. '
            'Consider using either an asynchronous main function and passing it to asyncio.run or '
        )
        raise AttributeError(msg)


_loop: Any = _LoopSentinel()

# --


def _authorize_required(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        for arg in args:
            if isinstance(arg, Client):
                if not arg.is_authorized():
                    client_func = f'Client.{fn.__name__}'
                    raise AuthRequired(f"{client_func!r} requires authorization")
                break
        return await fn(*args, **kwargs)

    return inner


class Client:
    def __init__(
        self,
        *,
        locale: Union[Locale, str] = Locale.american_english,
    ) -> None:
        self.locale: Locale = try_enum(Locale, locale) if isinstance(locale, str) else locale
        self.loop: asyncio.AbstractEventLoop = _loop
        self.http: HTTPClient = HTTPClient(self.loop)
        self.valorant_api: ValorantAPIClient = ValorantAPIClient(self.http._session, self.locale)
        self.me: ClientUser = MISSING
        self._closed: bool = False
        self._is_authorized: bool = False
        self._ready: asyncio.Event = MISSING
        self._version: ValorantAPIVersion = MISSING
        # self._season: Season = MISSING
        # self._act: Season = MISSING

    async def __aenter__(self) -> Self:
        await self.init()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if not self.is_closed():
            await self.close()

    @property
    def version(self) -> ValorantAPIVersion:
        return self._version

    async def wait_until_ready(self) -> None:
        """|coro|
        Waits until the client's internal cache is all ready.
        """
        if self._ready is not MISSING:
            await self._ready.wait()
        else:
            raise RuntimeError(
                'Client has not been properly initialised. '
                'Please use the authorize method or asynchronous context manager before calling this method'
            )

    async def init(self) -> None:
        _log.debug('initializing client')

        loop = asyncio.get_running_loop()
        self.loop = loop
        self.http.loop = loop

        # valorant-api
        self.loop.create_task(self.valorant_api.init())
        try:
            await asyncio.wait_for(self.valorant_api.wait_until_ready(), timeout=30)
        except asyncio.TimeoutError:
            raise RuntimeError('Valorant API did not become ready in time')
        else:
            self._version = self.valorant_api.version
            self.http.riot_client_version = self._version.riot_client_version

        _log.debug('client initialized')

    async def close(self) -> None:
        """|coro|

        Closes the client session and logs out.
        """
        if self._closed:
            return
        self._closed = True
        await self.http.close()
        await self.valorant_api.close()

    def clear(self) -> None:
        """Clears the internal cache."""
        self._closed = False
        self._ready = MISSING
        self.http.clear()
        self._is_authorized = False
        # self.user = MISSING
        # self.season = MISSING
        # self.act = MISSING

    def is_ready(self) -> bool:
        """:class:`bool`: Specifies if the client's internal cache is ready for use."""
        return self._ready is not MISSING and self._ready.is_set()

    def is_closed(self) -> bool:
        """:class:`bool`: Indicates if the client is closed."""
        return self._closed

    def is_authorized(self) -> bool:
        """:class:`bool`: Whether the client is authorized."""
        return self._is_authorized

    async def _login(self, username: str, password: str) -> None:
        _log.info('logging using username and password')
        self._ready = asyncio.Event()
        data = await self.http.static_login(username, password)
        self.me = me = ClientUser(data=data)
        self._is_authorized = True
        self._ready.set()
        _log.info('Logged as %s', me.display_name)

    async def authorize(self, username: str, password: str) -> None:
        """|coro|

        Authorize the client with the given username and password.

        Parameters
        -----------
        username: :class:`str`
           The username of the account to authorize.
        password: :class:`str`
            The password of the account to authorize.
        """

        if username is None or password is None:
            raise ValueError('Username or password cannot be None')

        await self._login(username, password)

    # fetch price and set season
    #     try:
    #         self.loop.create_task(self._set_season())
    #     except Exception as e:
    #         _log.exception('Failed to set season', exc_info=e)

    @_authorize_required
    async def fetch_store_front(self) -> StoreFront:
        data = await self.http.store_fetch_storefront()
        return StoreFront(self, data)

    @_authorize_required
    async def fetch_wallet(self) -> Wallet:
        data = await self.http.store_fetch_wallet()
        return Wallet(self, data)

    @_authorize_required
    async def fetch_entitlements(self) -> Entitlements:
        data = await self.http.store_fetch_entitlements()
        return Entitlements(self, data)

    @_authorize_required
    async def fetch_offers(self) -> Offers:
        data = await self.http.store_fetch_offers()
        return Offers(self, data)
