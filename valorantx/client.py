# Copyright (c) 2023-present STACiA,  2021-present Rapptz
# Licensed under the MIT

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List, Optional, Type, TypeVar, Union

from . import utils
from .enums import Locale, QueueType, Region, SeasonType, try_enum
from .errors import RiotAuthRequired
from .http import HTTPClient
from .models.account_xp import AccountXP
from .models.config import Config
from .models.content import Content
from .models.contracts import Contracts
from .models.coregame import CoreGameMatch, CoreGamePlayer
from .models.daily_ticket import DailyTicket
from .models.esports import ScheduleLeague, TournamentStanding
from .models.favorites import Favorites
from .models.loadout import Loadout
from .models.match import MatchDetails, MatchHistory
from .models.mmr import MatchmakingRating
from .models.name_service import NameService
from .models.party import Party, PartyPlayer
from .models.patchnotes import PatchNotes
from .models.pregame import PreGameMatch, PreGamePlayer
from .models.premiers import Conference, Eligibility, PremierPleyer, PremierSeason, Roster
from .models.store import AgentStore, Entitlements, Offers, StoreFront, Wallet
from .models.user import ClientUser
from .valorant_api_client import Client as ValorantAPIClient

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import ParamSpec, Self

    from .models.seasons import Season
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
Coro = Coroutine[Any, Any, T]

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


def _authorize_required(fn: Callable[P, Coro[T]]) -> Callable[P, Coro[T]]:
    async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        for arg in args:
            if isinstance(arg, Client):
                if not arg.is_authorized():
                    func = f'{arg.__class__.__name__}.{fn.__name__}'
                    raise RiotAuthRequired(f"{func!r} requires authorization")
                break
        return await fn(*args, **kwargs)

    return inner


class Client:
    def __init__(
        self,
        *,
        region: Region = MISSING,
        locale: Locale = Locale.american_english,
        re_authorize: bool = True,
    ) -> None:
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
        self.re_authorize: bool = re_authorize
        self.loop: asyncio.AbstractEventLoop = _loop
        self.http: HTTPClient = HTTPClient(self.loop, region=region, re_authorize=re_authorize)
        self.valorant_api: ValorantAPIClient = ValorantAPIClient(self.http._session, self.locale)
        self.me: ClientUser = MISSING
        self._closed: bool = False
        self._authorized: asyncio.Event = MISSING
        self._ready: asyncio.Event = MISSING
        self._version: Version = MISSING
        self._season: Season = MISSING
        self._act: Season = MISSING
        self._configs: Dict[Region, Config] = {}
        self._tasks: Dict[str, asyncio.Task[Any]] = {}

    async def __aenter__(self) -> Self:
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

    @property
    def season(self) -> Season:
        return self._season

    @property
    def act(self) -> Season:
        return self._act

    @property
    def configs(self) -> Dict[Region, Config]:
        return self._configs

    def get_config(self, region: Optional[Region] = None) -> Optional[Config]:
        """Gets the config for the given region.

        Parameters
        ----------
        region: Optional[:class:`Region`]
            The region to get the config for.

        Returns
        -------
        Optional[:class:`Config`]
            The config for the given region.
        """
        if region is None:
            region = self.region
        return self._configs.get(region)

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

    async def wait_until_authorized(self) -> None:
        """|coro|
        Waits until the client's internal cache is all ready.
        """
        if self._authorized is not MISSING:
            await self._authorized.wait()
        else:
            raise RuntimeError(
                'Client has not been properly initialised. '
                'Please use the authorize method or asynchronous context manager before calling this method'
            )

    async def _init(self) -> None:
        _log.debug('initializing client')

        loop = asyncio.get_running_loop()
        self.loop = loop
        self.http.loop = loop
        self._ready = asyncio.Event()
        self._authorized = asyncio.Event()

        # valorant-api
        await self.valorant_api.init()

        try:
            await asyncio.wait_for(self.valorant_api.wait_until_ready(), timeout=30)
        except asyncio.TimeoutError:
            raise RuntimeError('Valorant API did not become ready in time')
        else:
            self._version = self.valorant_api.version
            HTTPClient.RIOT_CLIENT_VERSION = self._version.riot_client_version
            _log.debug('assets valorant version: %s', self._version.version)

        self._tasks['after_authorize'] = self.loop.create_task(
            self._init_after_authorize(), name='valorantx: after_authorize'
        )

        _log.debug('client initialized')

    async def _init_after_authorize(self) -> None:
        await self.wait_until_authorized()

        # fetch offers and insert into items
        offers = await self.fetch_store_offers()
        self.valorant_api.insert_cost(offers)

        # fetch current season and act
        content = await self.fetch_content()
        for season_content in reversed(content.seasons):
            if not season_content.is_active():
                continue

            season = self.valorant_api.get_season(season_content.id)
            if season is not None:
                if season_content.type == SeasonType.episode:
                    self._season = season
                elif season_content.type == SeasonType.act:
                    self._act = season

        # fetch configs
        for region in Region:
            if region is Region.PBE:
                continue
            if region is self._configs:
                continue
            config = await self.fetch_config(region)
            self._configs[region] = config

        self._ready.set()

    async def close(self) -> None:
        """|coro|

        Closes the client session and logs out.
        """
        if self._closed:
            return
        self._closed = True

        await self.valorant_api.close()
        await self.http.close()
        if self._ready is not MISSING:
            self._ready.clear()

        if self._authorized is not MISSING:
            self._authorized.clear()

        for task in self._tasks.values():
            task.cancel()

        self.loop = MISSING

    def clear(self) -> None:
        """Clears the internal cache."""
        self._closed = False
        self._ready = MISSING
        self.http.clear()
        self._authorized = MISSING
        self.me = MISSING
        self._version = MISSING
        self._season = MISSING
        self._act = MISSING

    def is_ready(self) -> bool:
        """:class:`bool`: Specifies if the client's internal cache is ready for use."""
        return self._ready is not MISSING and self._ready.is_set()

    def is_closed(self) -> bool:
        """:class:`bool`: Indicates if the client is closed."""
        return self._closed

    def is_authorized(self) -> bool:
        """:class:`bool`: Whether the client is authorized."""
        return self._authorized is not MISSING and self._authorized.is_set()

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

        if self.loop is _loop:
            await self._init()

        _log.info('logging using username and password')
        data = await self.http.static_login(username, password, remember=remember)
        self.me = me = ClientUser(data=data)
        self._authorized.set()
        _log.info('logged as %s', me.riot_id)

        await self.wait_until_ready()

    async def authorize_from_data(self, auth_data: Dict[str, Any]) -> None:
        """|coro|

        Authorize the client with the given data.

        Parameters
        -----------
        data: :class:`Dict[str, Any]`
           The data of the account to authorize.
        """

        _log.info('logging using auth data')

        if self.loop is _loop:
            await self._init()

        data = await self.http.cookie_login(auth_data)
        self.me = me = ClientUser(data=data)
        self._authorized.is_set()
        _log.info('logged as %s', me.riot_id)

        await self.wait_until_ready()

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

        data = await self.http.get_patch_notes(locale)

        return PatchNotes(state=self.valorant_api.cache, data=data, locale=locale)

    # config

    @_authorize_required
    async def fetch_config(self, region: Optional[Region] = None) -> Config:
        """|coro|

        Fetches the config for the current user.

        Returns
        -------
        :class:`Config`
            The config for the current user.
        """
        data = await self.http.get_config(region)
        return Config(data)

    # name service endpoints

    @_authorize_required
    async def fetch_player_name_by_puuid(self, puuid: Union[List[str], str]) -> List[NameService]:
        data = await self.http.get_name_service_players(puuid)
        return [NameService(data=name) for name in data]

    # store endpoints

    @_authorize_required
    async def fetch_storefront(self) -> StoreFront:
        data = await self.http.post_store_storefront()
        return StoreFront(self.valorant_api.cache, data)

    @_authorize_required
    async def fetch_wallet(self) -> Wallet:
        data = await self.http.get_store_wallet()
        return Wallet(self.valorant_api.cache, data)

    @_authorize_required
    async def fetch_entitlements(self) -> Entitlements:
        data = await self.http.get_store_entitlements()
        return Entitlements(self, data)

    @_authorize_required
    async def fetch_store_offers(self) -> Offers:
        data = await self.http.get_store_offers()
        return Offers(self.valorant_api.cache, data)

    @_authorize_required
    async def fetch_agent_store(self) -> AgentStore:
        data = await self.http.get_store_storefronts_agent()
        return AgentStore(self, data['AgentStore'])

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
        data = await self.http.get_contracts()
        return Contracts(client=self, data=data)

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
        data = await self.http.get_favorites()
        return Favorites(state=self.valorant_api.cache, data=data)

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
    async def fetch_content(self) -> Content:
        """|coro|

        Fetches the content for the current version of Valorant.

        Returns
        -------
        :class:`Content`
            The content for the current version of Valorant.
        """
        data = await self.http.get_content()
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
        data = await self.http.get_account_xp_player()
        return AccountXP(self, data)

    @_authorize_required
    async def fetch_loudout(self) -> Loadout:
        favorites = await self.fetch_favorites()
        data = await self.http.get_personal_player_loadout()
        return Loadout(self, data, favorites=favorites)

    # @_authorize_required
    # async def put_loadout(self, loadout: LoadoutBuilder) -> None:
    #     await self.http.put_personal_player_loadout(loadout)
    #     pass

    @_authorize_required
    async def fetch_mmr(self, puuid: Optional[str] = None) -> MatchmakingRating:
        """|coro|

        Fetches the MMR for the current user or a given user.

        Parameters
        ----------
        puuid: Optional[:class:`str`]
            The puuid of the user to fetch the MMR for.

        Returns
        -------
        :class:`MatchmakingRating`
            The MMR for the current user or a given user.
        """
        data = await self.http.get_mmr_player(puuid)
        return MatchmakingRating(self, data)

    @_authorize_required
    async def fetch_match_history(
        self,
        puuid: Optional[str] = None,
        queue: Optional[Union[str, QueueType]] = None,
        *,
        start: int = 0,
        end: int = 15,
        with_details: bool = True,
    ) -> MatchHistory:
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
            Whether to fetch the match details for the match history.

        Returns
        -------
        :class:`MatchHistory`
            The match history for the current user or a given user.

        Raises
        ------
        HTTPException
            Fetching the match history failed.
        NotFound
            The match history for the given user could not be found.
        """
        if isinstance(queue, QueueType):
            queue = queue.value
        data = await self.http.get_match_history(puuid, start, end, queue)
        history = MatchHistory(client=self, data=data)
        if with_details:
            await history.fetch_details()
        return history

    @_authorize_required
    async def fetch_match_details(self, match_id: str, /) -> MatchDetails:
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
        raises
        ------
        HTTPException
            Fetching the match details failed.
        NotFound
            The match details for the given match could not be found.
        """
        data = await self.http.get_match_details(match_id)
        return MatchDetails(client=self, data=data)

    # party

    @_authorize_required
    async def fetch_party(self, party_id: Optional[str] = None, /) -> Party:
        if party_id is None:
            party_player = await self.fetch_party_player()
            party_id = party_player.current_party_id

        data = await self.http.get_party(party_id=party_id)
        party = Party(client=self, data=data)
        # await party.update_member_display_name()
        return party

    @_authorize_required
    async def fetch_party_player(self) -> PartyPlayer:
        data = await self.http.get_party_player()
        return PartyPlayer(client=self, data=data)

    # @_authorize_required
    # async def party_request_to_join(self, party_id: str) -> Any:
    #     return

    # pre game

    @_authorize_required
    async def fetch_pregame_player(self) -> PreGamePlayer:
        data = await self.http.get_pregame_player()
        return PreGamePlayer(client=self, data=data)

    @_authorize_required
    async def fetch_pregame_match(self, match_id: str, /) -> PreGameMatch:
        data = await self.http.get_pregame_match(match_id)
        return PreGameMatch(client=self, data=data)

    # core game

    @_authorize_required
    async def fetch_coregame_player(self) -> CoreGamePlayer:
        data = await self.http.get_coregame_player()
        return CoreGamePlayer(client=self, data=data)

    @_authorize_required
    async def fetch_coregame_match(self, match_id: str, /) -> CoreGameMatch:
        data = await self.http.get_coregame_match(match_id)
        return CoreGameMatch(client=self, data=data)

    # premier

    @_authorize_required
    async def fetch_premier_season(self) -> PremierSeason:
        data = await self.http.get_premier_seasons(active_season=True)
        return PremierSeason(data)

    @_authorize_required
    async def fetch_premier_seasons(self) -> List[PremierSeason]:
        data = await self.http.get_premier_seasons(active_season=False)
        return [PremierSeason(season) for season in data['PremierSeasons']]

    @_authorize_required
    async def fetch_premier_player(self, puuid: Optional[str] = None) -> PremierPleyer:
        data = await self.http.get_premier_player(puuid)
        return PremierPleyer(self, data)

    @_authorize_required
    async def fetch_premier_eligibility(self) -> Eligibility:
        data = await self.http.get_premier_eligibility()
        return Eligibility(data)

    @_authorize_required
    async def fetch_premier_conference(self) -> List[Conference]:
        data = await self.http.get_premier_conferences()
        return [Conference(conference) for conference in data['PremierConferences']]

    @_authorize_required
    async def fetch_premier_roster(self, roster_id: Optional[str] = None) -> Roster:
        if roster_id is None:
            roster_id = (await self.fetch_premier_player()).roster_id
        data = await self.http.get_premier_roster_v2(roster_id)
        return Roster(self, data)

    # daily ticket

    @_authorize_required
    async def fetch_daily_ticket(self, *, renew: bool = False) -> DailyTicket:
        if renew:
            data = await self.http.post_daily_ticket()
        else:
            data = await self.http.get_daily_ticket()
        return DailyTicket(self, data)

    # esports

    @_authorize_required
    async def fetch_esports_schedule(
        self,
        league_id: str,
        tournament_id: str,
        *,
        locale: Locale = Locale.american_english,
    ) -> ScheduleLeague:
        data = await self.http.get_epsport_schedule(league_id, tournament_id, locale=locale.value)
        schedule = ScheduleLeague(self, data)
        await schedule.refresh_teams()
        return schedule

    @_authorize_required
    async def fetch_esport_tournament_standings(
        self,
        tournament_id: str,
        *,
        locale: Locale = Locale.american_english,
    ) -> List[TournamentStanding]:
        data = await self.http.get_esport_tournament_standings(tournament_id, locale=locale.value)
        return [TournamentStanding(self, standing) for standing in data['TournamentStandings']]
