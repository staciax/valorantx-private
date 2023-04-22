# Copyright (c) 2023-present STACiA,  2021-present Rapptz
# Licensed under the MIT

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
from .enums import Locale, Region, try_enum  # ItemType, QueueType, SeasonType,
from .errors import AuthRequired
from .http import HTTPClient
from .models.contracts import Contracts
from .models.patchnotes import PatchNotes
from .models.store import Entitlements, Offers, StoreFront, Wallet
from .models.user import ClientUser
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
#     Currency,
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
#     Party,
#     PartyPlayer,
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
#     Weapon,
# )

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import ParamSpec, Self

    from .models.version import Version

    P = ParamSpec('P')
else:
    P = TypeVar('P')

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
            'using asynchronous initialisation with the async with context manager or the init method.'
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
    def __init__(self, *, region: Region = MISSING, locale: Locale = Locale.american_english) -> None:
        if region is MISSING:
            _log.warning(
                'You did not specify a region. The region will be checked automatically.'
                'This may cause some functions to not work as you intended.'
                'For example, client.fetch_store_front()'
            )
        if region is Region.PBE:
            _log.info('You are using the Public Beta Environment (PBE) server. Are you sure?')
        self.region: Region = region
        self.locale: Locale = locale
        self.loop: asyncio.AbstractEventLoop = _loop
        self.http: HTTPClient = HTTPClient(self.loop, region=region)
        self.valorant_api: ValorantAPIClient = ValorantAPIClient(self.http._session, self.locale)
        self.me: ClientUser = MISSING
        self._closed: bool = False
        self._is_authorized: bool = False
        self._ready: asyncio.Event = MISSING
        self._version: Version = MISSING
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
    def version(self) -> Version:
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
            _log.debug('assets valorant version: %s', self._version.version)

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

    async def _login(self, username: str, password: str, *, remember: bool) -> None:
        _log.info('logging using username and password')
        self._ready = asyncio.Event()
        data = await self.http.static_login(username, password, remember=remember)
        self.me = me = ClientUser(data=data)
        self._is_authorized = True
        self._ready.set()
        _log.info('Logged as %s', me.riot_id)

    async def authorize(self, username: str, password: str, *, remember: bool = False) -> None:
        """|coro|

        Authorize the client with the given username and password.

        Parameters
        -----------
        username: :class:`str`
           The username of the account to authorize.
        password: :class:`str`
            The password of the account to authorize.
        """

        if not username or not password:
            raise ValueError('username and password must be provided')

        await self._login(username, password, remember=remember)

        # TODO: below to asyncio.create_task
        # insert items cost
        offers = await self.fetch_offers()
        self.valorant_api.insert_cost(offers)
        # TODO: set season and act
        # fetch price and set season
        #     try:
        #         self.loop.create_task(self._set_season())
        #     except Exception as e:
        #         _log.exception('Failed to set season', exc_info=e)

    # patch notes endpoint

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

        # endpoint is not available for chinese
        locale = Locale.taiwan_chinese if locale is Locale.chinese else locale

        data = await self.http.fetch_patch_notes(locale)

        return PatchNotes(state=self.valorant_api._cache, data=data, locale=locale)

    # store endpoints

    @_authorize_required
    async def fetch_store_front(self) -> StoreFront:
        data = await self.http.store_fetch_storefront()
        return StoreFront(self.valorant_api._cache, data)

    @_authorize_required
    async def fetch_wallet(self) -> Wallet:
        data = await self.http.store_fetch_wallet()
        return Wallet(self.valorant_api._cache, data)

    @_authorize_required
    async def fetch_entitlements(self) -> Entitlements:
        data = await self.http.store_fetch_entitlements()
        return Entitlements(self.valorant_api._cache, data)

    @_authorize_required
    async def fetch_offers(self) -> Offers:
        data = await self.http.store_fetch_offers()
        return Offers(data)

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
        return Contracts(state=self.valorant_api._cache, data=data)

    # favorite endpoints

    @_authorize_required
    async def fetch_favorites(self) -> ...:
        """|coro|

        Fetches the favorites items for the current user.

        Returns
        -------
        :class:`Favorites`
            The favorites items for the current user.
        """
        data = await self.http.favorites_fetch()
        import json

        with open('favorites.json', 'w') as f:
            json.dump(data, f, indent=4)

    # @_authorize_required
    # async def add_favorite(self, item: Union[str, Buddy, PlayerCard, Skin, Spray, LevelBorder]) -> Favorites:
    #     """|coro|

    #     Adds a favorite item for the current user.

    #     Parameters
    #     ----------
    #     item: Union[:class:`str`, :class:`Buddy`, :class:`PlayerCard`, :class:`Skin`, :class:`Spray`]
    #         The item to add as a favorite.

    #     Returns
    #     -------
    #     :class:`Favorites`
    #         The favorites items for the current user.
    #     """
    #     if isinstance(item, (Buddy, PlayerCard, Skin, Spray, LevelBorder)):
    #         uuid = item.uuid
    #     else:
    #         uuid = item if utils.is_uuid(item) else ''
    #     data = await self._http.favorite_post(uuid)
    #     return Favorites(client=self, data=data)

    # @_authorize_required
    # async def remove_favorite(self, item: Union[str, Buddy, PlayerCard, Skin, Spray, LevelBorder]) -> Favorites:
    #     """|coro|

    #     Removes a favorite item for the current user.

    #     Parameters
    #     ----------
    #     item: Union[:class:`str`, :class:`Buddy`, :class:`PlayerCard`, :class:`Skin`, :class:`Spray`, :class:`LevelBorder`]
    #         The item to remove as a favorite.

    #     Returns
    #     -------
    #     :class:`Favorites`
    #         The favorites items for the current user.
    #     """
    #     if isinstance(item, (Buddy, PlayerCard, Skin, Spray, LevelBorder)):
    #         uuid = item.uuid
    #     else:
    #         uuid = item if utils.is_uuid(item) else ''
    #     data = await self.http.favorite_delete(uuid)
    #     return Favorites(client=self, data=data)

    # PVP endpoints

    @_authorize_required
    async def fetch_content(self) -> ...:  # Content
        """|coro|

        Fetches the content for the current version of Valorant.

        Returns
        -------
        :class:`Content`
            The content for the current version of Valorant.
        """
        data = await self.http.fetch_content()
        import json

        with open('content.json', 'w') as f:
            json.dump(data, f, indent=4)
        # return Content(client=self, data=data)

    @_authorize_required
    async def fetch_account_xp(self) -> ...:  # AccountXP
        """|coro|

        Fetches the account XP for the current user.

        Returns
        -------
        :class:`AccountXP`
            The account XP for the current user.
        """
        data = await self.http.fetch_account_xp()
        import json

        with open('account_xp.json', 'w') as f:
            json.dump(data, f, indent=4)
        # return AccountXP(client=self, data=data)

    @_authorize_required
    async def fetch_collection(self, *, with_xp: bool = True, with_favorite: bool = True) -> ...:  # Collection
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
        import json

        with open('player_loadout.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        # collection = Collection(client=self, data=data)

        # if with_xp:
        #     await collection.fetch_account_xp()

        # if with_favorite:
        #     await collection.fetch_favorites()

        # return collection

    # @_authorize_required
    # async def put_loadout(self, loadout: Mapping[str, Any]) -> None:  # TODO: loadout object
    #     """|coro|

    #     Puts the loadout for the current user.

    #     Parameters
    #     ----------
    #     loadout: :class:`Mapping`
    #         The loadout to put.

    #     Returns
    #     -------
    #     :class:`Any`
    #         The response from the API.
    #     """
    #     # await self.http.put_player_loadout(loadout)
    #     pass

    @_authorize_required
    async def fetch_mmr(self, puuid: Optional[str] = None) -> ...:  # MMR
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
        import json

        with open('mmr.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        # return MMR(client=self, data=data)

    @_authorize_required
    async def fetch_match_history(
        self,
        # puuid: Optional[str] = None,
        # queue: Optional[Union[str, QueueType]] = None,
        # *,
        # start: int = 0,
        # end: int = 15,
        # with_details: bool = True,
    ) -> ...:  # Optional[MatchHistory]
        data = await self.http.fetch_match_history(self.me.puuid, 0, 15, 'competitive')
        import json

        with open('match_history.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        # history = MatchHistory(client=self, data=data) if data else None
        # if with_details and history is not None:
        #     await history.fetch_details()
        # return history

    @_authorize_required
    async def fetch_match_details(self, match_id: str) -> ...:  # Optional[MatchDetails]
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
        import json

        with open('match_details.json', 'w') as f:
            json.dump(match_details, f, indent=4, ensure_ascii=False)
        # return MatchDetails(client=self, data=match_details)

    # # party endpoint

    # @_authorize_required
    # async def fetch_party(self, party_id: Optional[Union[Party, PartyPlayer, str]] = None) -> Party:
    #     if party_id is None:
    #         party_id = await self.fetch_party_player()

    #     if isinstance(party_id, PartyPlayer):
    #         party_id = party_id.id

    #     data = await self.http.fetch_party(party_id=str(party_id))
    #     party = Party(client=self, data=data)
    #     await party.update_member_display_name()
    #     return party

    # @_authorize_required
    # async def fetch_party_player(self) -> PartyPlayer:
    #     data = await self.http.party_fetch_player()
    #     return PartyPlayer(client=self, data=data)

    # @_authorize_required
    # async def party_request_to_join(self, party_id: str) -> Any:
    #     return ...

    # @_authorize_required
    # async def party_leave_from_party(self, party_id: str) -> Any:
    #     return ...

    # # pre game lobby endpoints

    # @_authorize_required
    # async def fetch_pregame_match(self, match: Optional[str] = None) -> Any:
    #     if match is None:
    #         match = await self.fetch_pregame_player()
    #     data = await self.http.pregame_fetch_match(match_id=match)

    # @_authorize_required
    # async def fetch_pregame_player(self) -> Any:
    #     data = await self.http.pregame_fetch_player()
