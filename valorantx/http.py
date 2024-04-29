# Copyright (c) 2023-present STACiA, 2021-present Rapptz
# Licensed under the MIT
# inspired by https://github.com/Rapptz/discord.py/blob/master/discord/http.py

from __future__ import annotations

import asyncio
import base64
import enum
import json
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Coroutine,
    Dict,
    List,
    Literal,
    Mapping,
    NoReturn,
    Optional,
    TypeVar,
    Union,
    overload,
)
from urllib.parse import quote as _uriquote

import aiohttp

from . import utils
from .auth import RiotAuth
from .enums import Locale, QueueType, Region, try_enum
from .errors import (
    BadRequest,
    Forbidden,
    HTTPException,
    InternalServerError,
    NotFound,
    RateLimited,
    RiotAuthenticationError,
)

# try:
#     import urllib3
# except ImportError:
#     pass
# else:
#     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#     # disable urllib3 warnings that might arise from making requests to 127.0.0.1
# enable when supported local client

MISSING = utils.MISSING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .types import (
        account_xp,
        config,
        content,
        contracts,
        coregame,
        daily_ticket,
        esports,
        favorites,
        loadout,
        match,
        mmr,
        name_service,
        party,
        pregame,
        premiers,
        store,
        user,
    )

    T = TypeVar('T')
    Response = Coroutine[Any, Any, T]

_log = logging.getLogger(__name__)


async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding='utf-8')

    try:
        if 'application/json' in response.headers['content-type']:
            return utils._from_json(text)
    except KeyError:
        pass

    # try to parse it as json anyway
    # some endpoints return plain text but it's actually json
    if isinstance(text, str):
        try:
            return utils._from_json(text)
        except json.JSONDecodeError:
            pass

    return text


class EndpointType(enum.Enum):
    pd = 0
    glz = 1
    shard = 2
    play_valorant = 3


# http-client inspired by https://github.com/Rapptz/discord.py/blob/master/discord/http.pyS


class Route:
    BASE_PD_URL: ClassVar[str] = 'https://pd.{shard}.a.pvp.net'
    BASE_GLZ_URL: ClassVar[str] = 'https://glz-{region}-1.{shard}.a.pvp.net'
    BASE_SHARD_URL: ClassVar[str] = 'https://shared.{shard}.a.pvp.net'
    BASE_PLAY_VALORANT_URL: ClassVar[str] = 'https://playvalorant.com'

    def __init__(
        self,
        method: str,
        path: str,
        region: Region = Region.AP,
        endpoint: EndpointType = EndpointType.pd,
        **parameters: Any,
    ) -> None:
        self.method = method
        self.path = path
        self.region = region
        self.endpoint = endpoint
        self.parameters = parameters

        url = ''
        if endpoint == EndpointType.pd:
            url = self.BASE_PD_URL.format(shard=str(region.shard)) + path
        elif endpoint == EndpointType.glz:
            url = self.BASE_GLZ_URL.format(region=str(region), shard=str(region)) + path
        elif endpoint == EndpointType.shard:
            url = self.BASE_SHARD_URL.format(shard=str(region.shard)) + path
        elif endpoint == EndpointType.play_valorant:
            url = self.BASE_PLAY_VALORANT_URL + path

        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url

    @classmethod
    def from_url(cls, method: str, url: str, **parameters: Any) -> Self:
        self = cls.__new__(cls)
        self.method = method
        self.url = url
        self.parameters = parameters
        if parameters:
            self.url = self.url.format_map({
                k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()
            })
        return self


class HTTPClient:
    RIOT_CLIENT_VERSION: ClassVar[str] = ''
    RIOT_CLIENT_PLATFORM: ClassVar[str] = base64.b64encode(
        json.dumps(
            {
                'platformType': 'PC',
                'platformOS': 'Windows',
                'platformOSVersion': '10.0.19042.1.256.64bit',
                'platformChipset': 'Unknown',
            },
            indent=4,
        ).encode()
    ).decode()

    def __init__(self, loop: asyncio.AbstractEventLoop, *, region: Region, re_authorize: bool) -> None:
        self.loop: asyncio.AbstractEventLoop = loop
        self._session: aiohttp.ClientSession = MISSING
        self.riot_auth: RiotAuth = RiotAuth()
        self._puuid: Optional[str] = None
        self.region: Region = region
        self.re_authorize: bool = re_authorize

    @property
    def puuid(self) -> Optional[str]:
        return self._puuid

    def clear(self) -> None:
        if self._session and self._session.closed:
            self._session = MISSING

    async def request(self, route: Route, **kwargs: Any) -> Any:
        method = route.method
        url = route.url

        headers = kwargs.pop('headers', await self.__build_headers())

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = utils._to_json(kwargs.pop('json'))

        kwargs['headers'] = headers

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None

        if self._session is MISSING:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=0),
                # raise_for_status=True
            )

        for tries in range(5):
            try:
                async with self._session.request(method, url, **kwargs) as response:
                    _log.debug('%s %s with %s has returned %s', method, url, kwargs.get('data'), response.status)
                    data = await json_or_text(response)
                    if 300 > response.status >= 200:
                        _log.debug('%s %s has received %s', method, url, data)
                        return data

                    if response.status == 400:
                        if tries < 4 and self.re_authorize:
                            if isinstance(data, dict) and data.get('errorCode') == 'BAD_CLAIMS':
                                try:
                                    await self.riot_auth.reauthorize()
                                except RiotAuthenticationError:
                                    ...
                                else:
                                    if 'headers' in kwargs:
                                        kwargs['headers'].update(await self.__build_headers())
                                    continue
                        raise BadRequest(response, data)

                    # we are being rate limited
                    if response.status == 429:
                        if not response.headers.get('Via') or isinstance(data, str):
                            # Banned by Cloudflare more than likely.
                            raise HTTPException(response, data)

                        raise RateLimited(response, data)

                    if response.status in {500, 502, 504, 524}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    if response.status == 403:
                        raise Forbidden(response, data)
                    elif response.status == 404:
                        raise NotFound(response, data)
                    elif response.status >= 500:
                        raise InternalServerError(response, data)
                    else:
                        raise HTTPException(response, data)

            except OSError as e:
                # Connection reset by peer
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise

        if response is not None:
            # We've run out of retries, raise.
            if response.status >= 500:
                raise InternalServerError(response, data)

            raise HTTPException(response, data)

        raise RuntimeError('Unreachable code in HTTP handling')

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def static_login(self, username: str, password: str) -> user.PartialUser:
        """Riot Auth login."""
        if self._session is MISSING:
            self._session = aiohttp.ClientSession()

        await self.riot_auth.authorize(username.strip(), password.strip())

        if self.region is MISSING:
            try:
                region = await self.riot_auth.fetch_region()  # fetch region
            except KeyError:
                self.region = Region.AP  # default to AP
                _log.warning('Could not find region for Riot Auth, defaulting to AP')
            else:
                self.region = try_enum(Region, region)

        self._puuid = self.riot_auth.puuid
        await self.__build_headers()

        data = {
            'puuid': self.riot_auth.puuid,
            'game_name': self.riot_auth.game_name,
            'tag_line': self.riot_auth.tag_line,
            'region': self.riot_auth.region,
        }
        return data  # type: ignore

    async def cookie_login(self, data: Dict[str, Any]) -> user.PartialUser:
        if self._session is MISSING:
            self._session = aiohttp.ClientSession()

        self.riot_auth.from_data(data)
        self._puuid = self.riot_auth.puuid
        self.region = try_enum(Region, self.riot_auth.region)
        await self.__build_headers()
        data = {
            'puuid': self.riot_auth.puuid,
            'game_name': self.riot_auth.game_name,
            'tag_line': self.riot_auth.tag_line,
            'region': self.riot_auth.region,
        }
        return data  # type: ignore

    async def token_login(self, data: Dict[str, Any]) -> RiotAuth:
        """Riot Auth login."""

        self.riot_auth.from_data(data)
        self._puuid = self.riot_auth.puuid
        await self.__build_headers()
        if self._session is MISSING:
            self._session = aiohttp.ClientSession()
        return self.riot_auth

    async def read_from_url(self, url: str) -> bytes:
        async with self._session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise NotFound(resp, 'asset not found')
            elif resp.status == 403:
                raise Forbidden(resp, 'cannot retrieve asset')
            else:
                raise HTTPException(resp, 'failed to get asset')

    async def text_from_url(self, url: str) -> str:
        async with self._session.get(url) as resp:
            if resp.status == 200:
                return await resp.text()
            elif resp.status == 404:
                raise NotFound(resp, 'asset not found')
            elif resp.status == 403:
                raise Forbidden(resp, 'cannot retrieve asset')
            else:
                raise HTTPException(resp, 'failed to get asset')

    # naming rule: METHOD_CATEGORY_ENDPONINT_NAME
    # if CATEGORY and ENDPOINT are the same, then just use CATEGORY
    # like get_leaderboard_leaderboard to get_leaderboard

    # play valorant endpoints

    def get_patch_notes(self, locale: Union[str, Locale] = Locale.american_english) -> Response[Mapping[str, Any]]:
        """
        FetchPatchNote
        Get the latest patch note
        """
        r = Route(
            'GET',
            '/page-data/{locale}/news/tags/patch-notes/page-data.json',
            self.region,
            EndpointType.play_valorant,
            locale=str(locale).lower(),
        )
        return self.request(r)

    # PVP endpoints

    def get_content(self) -> Response[content.Content]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        return self.request(Route('GET', '/content-service/v3/content', self.region, EndpointType.shard))

    def get_account_xp_player(self) -> Response[account_xp.AccountXP]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        return self.request(
            Route('GET', '/account-xp/v1/players/{puuid}', self.region, EndpointType.pd, puuid=self.puuid)
        )

    def get_personal_player_loadout(self) -> Response[loadout.Loadout]:
        """
        playerLoadoutUpdate
        Get the player's current loadout
        """
        return self.request(
            Route(
                'GET',
                '/personalization/v2/players/{puuid}/playerloadout',
                self.region,
                EndpointType.pd,
                puuid=self.puuid,
            )
        )

    def put_personal_player_loadout(self, loadout: Mapping[str, Any]) -> Response[loadout.Loadout]:
        """
        playerLoadoutUpdate
        Use the values from self._fetch_player_loadout() excluding properties like subject and version.
        Loadout changes take effect when starting a new game
        """
        r = Route(
            'PUT',
            '/personalization/v2/players/{puuid}/playerloadout',
            self.region,
            EndpointType.pd,
            puuid=self.puuid,
        )
        return self.request(r, json=loadout)

    def get_mmr_player(self, puuid: Optional[str] = None) -> Response[mmr.MatchmakingRating]:
        """
        MMR_FetchPlayer
        Get the match making rating for a player
        """
        puuid = self.__check_puuid(puuid)
        return self.request(Route('GET', '/mmr/v1/players/{puuid}', self.region, EndpointType.pd, puuid=puuid))

    def get_match_history(
        self,
        puuid: Optional[str] = None,
        start_index: int = 0,
        end_index: int = 15,
        queue_id: Optional[Union[str, QueueType]] = None,
    ) -> Response[match.MatchHistory]:
        """
        MatchHistory_FetchMatchHistory
        Get recent matches for a player
        There are 3 optional query parameters: start_index, end_index, and queue_id.queue can be one of null,
        competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        """

        puuid = self.__check_puuid(puuid)
        # if isinstance(queue_id, str):
        #     queue_id = try_enum(QueueID, queue_id, '')

        if isinstance(queue_id, QueueType):
            queue_id = str(queue_id)

        r = Route('GET', '/match-history/v1/history/{puuid}', self.region, EndpointType.pd, puuid=puuid)
        params = {
            'startIndex': start_index,
            'endIndex': end_index,
        }
        if queue_id is not None:
            params['queue'] = queue_id  # type: ignore
        return self.request(r, params=params)

    def get_match_details(self, match_id: str) -> Response[match.MatchDetails]:
        """
        Get the full info for a previous match
        Includes everything that the in-game match details screen shows including damage and kill positions,
        same as the official API w/ a production key
        """
        return self.request(
            Route(
                'GET',
                '/match-details/v1/matches/{match_id}',
                self.region,
                EndpointType.pd,
                match_id=match_id,
            )
        )

    def get_mmr_player_competitive_updates(
        self,
        puuid: Optional[str] = None,
        start_index: int = 0,
        end_index: int = 15,
        queue_id: Union[str, QueueType] = QueueType.competitive,
    ) -> Response[mmr.PlayerCompetitiveUpdates]:
        """
        MMR_FetchCompetitiveUpdates
        Get recent games and how they changed ranking
        There are 3 optional query parameters: start_index, end_index, and queue_id. queue can be one of null,
        competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        """
        puuid = self.__check_puuid(puuid)
        if isinstance(queue_id, QueueType):
            queue_id = str(queue_id)
        r = Route('GET', '/mmr/v1/players/{puuid}/competitiveupdates', self.region, EndpointType.pd, puuid=puuid)
        params = {'startIndex': start_index, 'endIndex': end_index}
        if queue_id is not None:
            params['queue'] = queue_id  # type: ignore

        return self.request(r, params=params)

    def get_mmr_leaderboard(
        self,
        season_id: Optional[str],
        start_index: int = 0,
        size: int = 510,
        query: Optional[str] = None,
        region: Optional[Region] = None,
    ) -> Response[mmr.Leaderboards]:
        """
        MMR_FetchLeaderboard
        Get the competitive leaderboard for a given season
        The query parameter query can be added to search for a username.
        """
        if season_id is None:
            raise ValueError('Season cannot be empty')

        region = region or self.region

        r = Route(
            'GET',
            '/mmr/v1/leaderboards/affinity/{shard}/queue/competitive/season/{season}',
            region,
            EndpointType.pd,
            shard=region.shard,
            season=season_id,
        )
        params: Dict[str, Any] = {'startIndex': start_index, 'size': size}
        if query is not None:
            params['query'] = query

        return self.request(r, params=params)

    def get_restrictions_penalties(self) -> Response[Mapping[str, Any]]:
        """
        Restrictions_FetchPlayerRestrictionsV3
        Checks for any gameplay penalties on the account
        """
        return self.request(Route('GET', '/restrictions/v3/penalties', self.region, EndpointType.pd))

    def get_contract_definitions_item_upgrades_v2(self) -> Response[Mapping[str, Any]]:
        """
        ItemProgressionDefinitionsV2_Fetch
        Get details for item upgrades
        """
        return self.request(Route('GET', '/contract-definitions/v2/item-upgrades', self.region, EndpointType.pd))

    def get_config(self, region: Optional[Region]) -> Response[config.Config]:
        """
        Config_FetchConfig
        Get various internal game configuration settings set by Riot
        """
        region = region or self.region
        return self.request(
            Route('GET', '/v1/config/{config_region}', region, EndpointType.shard, config_region=region.value),
        )

    def get_name_service_players(self, puuid: Union[List[str], str]) -> Response[List[name_service.NameServive]]:
        """
        Name_service
        get player name tag by puuid
        NOTE:
        format ['PUUID']
        """

        if isinstance(puuid, str):
            puuid = [puuid]

        return self.request(Route('PUT', '/name-service/v2/players', self.region, EndpointType.pd), json=puuid)

    # contract endpoints

    def get_contract_definitions(self) -> Response[Mapping[str, Any]]:
        """
        ContractDefinitions_Fetch
        Get names and descriptions for contracts
        """
        return self.request(Route('GET', '/contract-definitions/v3/definitions', self.region, EndpointType.pd))

    def get_contracts(self) -> Response[contracts.Contracts]:
        """
        Contracts_Fetch
        Get a list of contracts and completion status including match history
        """
        return self.request(
            Route('GET', '/contracts/v1/contracts/{puuid}', self.region, EndpointType.pd, puuid=self.puuid)
        )

    def post_contracts_special(self, contract_id: str) -> Response[contracts.Contracts]:
        """
        Contracts_Activate
        Activate a particular contract

        {contract id}: The ID of the contract to activate. Can be found from the ContractDefinitions_Fetch endpoint.
        """
        r = Route(
            'POST',
            '/contracts/v1/contracts/{puuid}/special/{contract}',
            self.region,
            EndpointType.pd,
            puuid=self.puuid,
            contract=contract_id,
        )
        return self.request(r)

    def get_contracts_definitions_story(self) -> Response[Mapping[str, Any]]:
        """
        ContractDefinitions_FetchActiveStory
        Get the battlepass contracts
        """
        return self.request(Route('GET', '/contract-definitions/v2/definitions/story', self.region, EndpointType.pd))

    def get_contract_definitions_item_upgrades(self) -> Response[Mapping[str, Any]]:
        """
        ItemProgressDefinitionsV2_Fetch
        Fetch definitions for skin upgrade progressions
        """
        return self.request(Route('GET', '/contract-definitions/v3/item-upgrades', self.region, EndpointType.pd))

    def post_contract_item_upgradess(self, progression_id: str) -> Response[Mapping[str, Any]]:
        """
        Contracts_UnlockItemProgressV2
        Unlock an item progression
        """
        return self.request(
            Route(
                'POST',
                '/contracts/v2/item-upgrades/{progression}/{puuid}',
                self.region,
                EndpointType.pd,
                puuid=self.puuid,
                progression=progression_id,
            )
        )

    # store endpoints

    def get_store_offers(self) -> Response[store.Offers]:
        """
        Store_GetOffers
        Get prices for all store items
        """
        return self.request(Route('GET', '/store/v1/offers/', self.region, EndpointType.pd))

    def get_store_storefront(self) -> Response[store.StoreFront]:
        """
        Store_GetStorefrontV2
        Get the currently available items in the store
        """
        return self.request(
            Route('GET', '/store/v2/storefront/{puuid}', self.region, EndpointType.pd, puuid=self.puuid)
        )

    def post_store_storefront(self) -> Response[store.StoreFront]:
        """
        Store_PostStorefrontV3
        Get the currently available items in the store
        """
        payload = {}
        return self.request(
            Route('POST', '/store/v3/storefront/{puuid}', self.region, EndpointType.pd, puuid=self.puuid), json=payload
        )

    def get_store_storefronts_agent(self) -> Response[store.AgentStoreFront]:
        """
        Store_GetAgentStorefront
        Get the currently available items in the store
        """
        r = Route('GET', '/store/v1/storefronts/agent', self.region, EndpointType.pd)
        return self.request(r)

    def get_store_wallet(self) -> Response[store.Wallet]:
        """
        Store_GetWallet
        Get amount of Valorant points and Radianite the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741
        and Radianite points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7
        """
        return self.request(Route('GET', '/store/v1/wallet/{puuid}', self.region, EndpointType.pd, puuid=self.puuid))

    def get_store_order(self, order_id: str) -> Response[Mapping[str, Any]]:
        """
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        """
        return self.request(Route('GET', '/store/v1/order/{order}', self.region, EndpointType.pd, order=order_id))

    def get_store_entitlements(
        self,
        item_type: Optional[str] = None,  # TODO: Union[str, ItemType]
    ) -> Response[store.Entitlements]:
        """
        Store_GetEntitlements
        List what the player owns (agents, skins, buddies, ect.)
        Correlate with the UUIDs in client.fetch_content() to know what items are owned
        NOTE: uuid to item type
        "e7c63390-eda7-46e0-bb7a-a6abdacd2433": "skin_level",
        "3ad1b2b2-acdb-4524-852f-954a76ddae0a": "skin_chroma",
        "01bb38e1-da47-4e6a-9b3d-945fe4655707": "agent",
        "f85cb6f7-33e5-4dc8-b609-ec7212301948": "contract_definition",
        "dd3bf334-87f3-40bd-b043-682a57a8dc3a": "buddy",
        "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475": "spray",
        "3f296c07-64c3-494c-923b-fe692a4fa1bd": "player_card",
        "de7caa6b-adf7-4588-bbd1-143831e786c6": "player_title",
        """

        r = Route(
            'GET',
            '/store/v1/entitlements/{puuid}' + (f'/{item_type}' if item_type is not None else ''),
            self.region,
            EndpointType.pd,
            puuid=self.puuid,
        )
        return self.request(r)

    # party endpoints

    def get_party_player(self) -> Response[party.Player]:
        """
        Party_FetchPlayer
        Get the Party ID that a given player belongs to
        """
        return self.request(
            Route('GET', '/parties/v1/players/{puuid}', self.region, EndpointType.glz, puuid=self.puuid)
        )

    def delete_party_remove_player(self, puuid: str) -> Response[NoReturn]:
        """
        Party_RemovePlayer
        Removes a player from the current party
        """
        puuid = self.__check_puuid(puuid)
        return self.request(Route('DELETE', '/parties/v1/players/{puuid}', self.region, EndpointType.glz, puuid=puuid))

    def get_party(self, party_id: str) -> Response[party.Party]:
        """
        Party_FetchParty
        Get details about a given party id
        """
        r = Route('GET', '/parties/v1/parties/{party_id}', self.region, EndpointType.glz, party_id=party_id)
        return self.request(r)

    def post_party_member_set_ready(self, party_id: str, ready: bool) -> Response[party.Party]:
        """
        Party_SetMemberReady
        Sets whether a party member is ready for queueing or not
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/setReady',
            self.region,
            EndpointType.glz,
            party_id=party_id,
            puuid=self.puuid,
        )
        payload = {'ready': ready}
        return self.request(r, json=payload)

    def post_party_refresh_competitive_tier(self, party_id: str) -> Response[party.Party]:
        """
        Party_RefreshCompetitiveTier
        Refreshes the competitive tier for a player
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/refreshCompetitiveTier',
            self.region,
            EndpointType.glz,
            party_id=party_id,
            puuid=self.puuid,
        )
        return self.request(r)

    def post_party_refresh_player_identity(self, party_id: str) -> Response[party.Party]:
        """
        Party_RefreshPlayerIdentity
        Refreshes the identity for a player
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/refreshPlayerIdentity',
            self.region,
            EndpointType.glz,
            party_id=party_id,
            puuid=self.puuid,
        )
        return self.request(r)

    def post_party_refresh_pings(self, party_id: str) -> Response[party.Party]:
        """
        Party_RefreshPings
        Refreshes the pings for a player
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/refreshPings',
            self.region,
            EndpointType.glz,
            party_id=party_id,
            puuid=self.puuid,
        )
        return self.request(r)

    def post_party_queue(self, party_id: str, queue_id: Union[QueueType, str]) -> Response[party.Party]:
        """
        Party_ChangeQueue
        Sets the matchmaking queue for the party
        """
        r = Route('POST', '/parties/v1/parties/{party_id}/queue', self.region, EndpointType.glz, party_id=party_id)
        payload = {'queueID': str(queue_id)}
        return self.request(r, json=payload)

    def post_party_start_custom_game(self, party_id: str) -> Response[party.Party]:
        """
        Party_StartCustomGame
        Starts a custom game
        """
        r = Route(
            'POST', '/parties/v1/parties/{party_id}/startcustomgame', self.region, EndpointType.glz, party_id=party_id
        )
        return self.request(r)

    def post_party_matchmaking_join(self, party_id: str) -> Response[party.Party]:
        """
        Party_EnterMatchmakingQueue
        Enters the matchmaking queue
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/matchmaking/join',
            self.region,
            EndpointType.glz,
            party_id=party_id,
        )
        return self.request(r)

    def post_party_matchmaking_leave(self, party_id: str) -> Response[party.Party]:
        """
        Party_LeaveMatchmakingQueue
        Leaves the matchmaking queue
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/matchmaking/leave',
            self.region,
            EndpointType.glz,
            party_id=party_id,
        )
        return self.request(r)

    def post_party_accessibility(self, party_id: str, open_join: bool) -> Response[party.Party]:
        """
        Party_SetAccessibility
        Changes the party accessibility to be open or closed
        """
        r = Route(
            'POST', '/parties/v1/parties/{party_id}/accessibility', self.region, EndpointType.glz, party_id=party_id
        )
        payload = {'accessibility': ('OPEN' if open_join else 'CLOSED')}
        return self.request(r, json=payload)

    def post_party_custom_game_settings(self, party_id: str, settings: Mapping) -> Response[Mapping[str, Any]]:
        """
        Party_SetCustomGameSettings
        Changes the settings for a custom game
        settings:
        {
            "Map": "/Game/Maps/Triad/Triad", # map url
            "Mode": "/Game/GameModes/Bomb/BombGameMode.BombGameMode_C", # url to game mode
            "UseBots": true, # this isn't used anymore :(
            "GamePod": "aresriot.aws-rclusterprod-use1-1.na-gp-ashburn-awsedge-1", # server
            "GameRules": null # I don't know what this is for
        }
        """
        # TODO: Object settings
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/customgamesettings',
            self.region,
            EndpointType.glz,
            party_id=party_id,
        )
        return self.request(r, json=settings)

    def post_party_invite_by_display_name(self, party_id: str, name: str, tag: str) -> Response[party.Party]:
        """
        Party_InviteToPartyByDisplayName
        Invites a player to the party with their display name
        omit the "#" in tag
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/invites/name/{name}/tag/{tag}',
            self.region,
            EndpointType.glz,
            party_id=party_id,
            name=name,
            tag=tag,
        )
        return self.request(r)

    def post_party_request_to_join(self, party_id: str, other_puuid: str) -> Response[Mapping[str, Any]]:
        """
        Party_RequestToJoinParty
        Requests to join a party
        """
        r = Route('POST', '/parties/v1/parties/{party_id}/request', self.region, EndpointType.glz, party_id=party_id)
        payload = {'Subjects': [other_puuid]}
        return self.request(r, json=payload)

    def post_party_decline_request(self, party_id: str, request_id: str) -> Response[party.Party]:
        """
        Party_DeclineRequest
        Declines a party request
        {request id}: The ID of the party request. Can be found from the Requests array on the Party_FetchParty endpoint.
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/request/{request_id}/decline',
            self.region,
            EndpointType.glz,
            party_id=party_id,
            request_id=request_id,
        )
        return self.request(r)

    def post_party_join(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_PlayerJoin
        Join a party
        """
        r = Route(
            'POST',
            '/parties/v1/players/{puuid}/joinparty/{party_id}',
            self.region,
            EndpointType.glz,
            puuid=self.puuid,
            party_id=party_id,
        )
        return self.request(r)

    def post_party_leave(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_PlayerLeave
        Leave a party
        """
        r = Route(
            'POST',
            '/parties/v1/players/{puuid}/leaveparty/{party_id}',
            self.region,
            EndpointType.glz,
            puuid=self.puuid,
            party_id=party_id,
        )
        return self.request(r)

    def get_party_fetch_custom_game_configs(self) -> Response[Mapping[str, Any]]:
        """
        Party_FetchCustomGameConfigs
        Get information about the available game modes
        """
        r = Route('GET', '/parties/v1/parties/customgameconfigs', self.region, EndpointType.glz)
        return self.request(r)

    def get_party_fetch_muc_token(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_FetchMUCToken
        Get a token for party chat
        """
        r = Route('GET', '/parties/v1/parties/{party_id}/muctoken', self.region, EndpointType.glz, party_id=party_id)
        return self.request(r)

    def get_party_fetch_voice_token(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_FetchVoiceToken
        Get a token for party voice
        """
        r = Route('GET', '/parties/v1/parties/{party_id}/voicetoken', self.region, EndpointType.glz, party_id=party_id)
        return self.request(r)

    def post_party_transfer_owner(self, party_id: str, puuid: str) -> Response[party.Party]:  # TODO: not sure
        """
        Party_TransferOwner
        Transfer party ownership
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/owner',
            self.region,
            EndpointType.glz,
            party_id=party_id,
            puuid=puuid,
        )
        return self.request(r)

    def delete_party_leave_from_party(self, party_id: str, puuid: str) -> Response[party.Party]:  # TODO: not sure
        """
        Party_LeaveFromParty
        Kick a player from the party
        """
        r = Route(
            'DELETE',
            '/parties/v1/parties/{party_id}/members/{puuid}',
            self.region,
            EndpointType.glz,
            party_id=party_id,
            puuid=puuid,
        )
        return self.request(r)

    # queue endpoints

    def get_queue_matchmaking_fetch_queue(self) -> Response[Mapping[str, Any]]:
        """
        QueueMatchmaking_FetchQueue
        Get information about the current queue
        """
        r = Route('GET', '/matchmaking/v1/queues/configs ', self.region, EndpointType.glz)
        return self.request(r)

    # favorite endpoints

    def get_favorites(self) -> Response[favorites.Favorites]:
        """
        FetchFavorite
        Get the favorite list of the authenticated user
        """
        r = Route('GET', '/favorites/v1/players/{puuid}/favorites', self.region, EndpointType.pd, puuid=self.puuid)
        return self.request(r)

    def post_favorites(self, item_id: str) -> Response[favorites.Favorites]:
        """
        PostFavorite
        Add a player to the favorite list of the authenticated user
        """
        r = Route('POST', '/favorites/v1/players/{puuid}/favorites', self.region, EndpointType.pd, puuid=self.puuid)
        payload = {'ItemID': item_id}
        return self.request(r, json=payload)

    def delete_favorites(self, item_id: str) -> Response[favorites.Favorites]:
        """
        DeleteFavorite
        Remove a player from the favorite list of the authenticated user
        """
        item_id_without_dashes = str(item_id).replace('-', '')
        r = Route(
            'DELETE',
            '/favorites/v1/players/{puuid}/favorites/{item_id}',
            self.region,
            EndpointType.pd,
            puuid=self.puuid,
            item_id=item_id_without_dashes,
        )
        return self.request(r)

    def post_favorites_modify(self) -> Response[favorites.Favorites]:
        """
        PostModifyFavorites
        Add a player to the favorite list of the authenticated user
        """
        r = Route(
            'POST', '/favorites/v1/players/{puuid}/favorites-batch', self.region, EndpointType.pd, puuid=self.puuid
        )
        payload = {}
        return self.request(r, json=payload)

    # pre game endpoints

    def get_pregame_player(self) -> Response[pregame.Player]:
        """
        Pregame_GetPlayer
        Get the ID of a game in the pre-game stage
        """
        r = Route('GET', '/pregame/v1/players/{puuid}', self.region, EndpointType.glz, puuid=self.puuid)
        return self.request(r)

    def get_pregame_match(self, match_id: str) -> Response[pregame.Match]:
        """
        Pregame_GetMatch
        Get info for a game in the pre-game stage
        """
        r = Route('GET', '/pregame/v1/matches/{match_id}', self.region, EndpointType.glz, match_id=match_id)
        return self.request(r)

    def get_pregame_match_loadouts(self, match_id: str) -> Response[pregame.Loadouts]:
        """
        Pregame_GetMatchLoadouts
        Get player skins and sprays for a game in the pre-game stage
        """
        r = Route('GET', '/pregame/v1/matches/{match_id}/loadouts', self.region, EndpointType.glz, match_id=match_id)
        return self.request(r)

    def get_pregame_chat_token(self, match_id: str) -> Response[Mapping[str, Any]]:
        """
        Pregame_FetchChatToken
        Get a chat token
        """
        r = Route('GET', '/pregame/v1/matches/{match_id}/chattoken', self.region, EndpointType.glz, match_id=match_id)
        return self.request(r)

    def get_pregame_voice_token(self, match_id: str) -> Response[Mapping[str, Any]]:
        """
        Pregame_FetchVoiceToken
        Get a voice token
        """
        r = Route('GET', '/pregame/v1/matches/{match_id}/voicetoken', self.region, EndpointType.glz, match_id=match_id)
        return self.request(r)

    def post_pregame_select_character(self, match_id: str, agent_id: str) -> Response[pregame.Match]:
        """
        Pregame_SelectCharacter
        Select an agent
        don't use this for instalocking :)
        """
        r = Route(
            'POST',
            '/pregame/v1/matches/{match_id}/select/{agent_id}',
            self.region,
            EndpointType.glz,
            match_id=match_id,
            agent_id=agent_id,
        )
        return self.request(r)

    def post_pregame_lock_character(self, match_id: str, agent_id: str) -> Response[pregame.Match]:
        """
        Pregame_LockCharacter
        Lock in an agent
        don't use this for instalocking :)
        """
        r = Route(
            'POST',
            '/pregame/v1/matches/{match_id}/lock/{agent_id}',
            self.region,
            EndpointType.glz,
            match_id=match_id,
            agent_id=agent_id,
        )
        return self.request(r)

    def post_pregame_quit_match(self, match_id: str) -> Response[NoReturn]:
        """
        Pregame_QuitMatch
        Quit a match in the pre-game stage
        """
        r = Route('POST', '/pregame/v1/matches/{match_id}/quit', self.region, EndpointType.glz, match_id=match_id)
        return self.request(r)

    # live game endpoints

    def get_coregame_player(self) -> Response[coregame.Player]:
        """
        CoreGame_FetchPlayer
        Get the game ID for an ongoing game the player is in
        """
        r = Route('GET', '/core-game/v1/players/{puuid}', self.region, EndpointType.glz, puuid=self.puuid)
        return self.request(r)

    def get_coregame_match(self, match_id: str) -> Response[coregame.Match]:
        """
        CoreGame_FetchMatch
        Get information about an ongoing game
        """
        r = Route('GET', '/core-game/v1/matches/{match_id}', self.region, EndpointType.glz, match_id=match_id)
        return self.request(r)

    def get_coregame_match_loadouts(self, match_id: str) -> Response[coregame.Loaouts]:
        """
        CoreGame_FetchMatchLoadouts
        Get player skins and sprays for an ongoing game
        """
        r = Route('GET', '/core-game/v1/matches/{match_id}/loadouts', self.region, EndpointType.glz, match_id=match_id)
        return self.request(r)

    def get_coregame_team_chat_muc_token(self, match_id: str) -> Response[Mapping[str, Any]]:
        """
        CoreGame_FetchTeamChatMUCToken
        Get a token for team chat
        """
        r = Route(
            'GET', '/core-game/v1/matches/{match_id}/teamchatmuctoken', self.region, EndpointType.glz, match_id=match_id
        )
        return self.request(r)

    def get_coregame_all_chat_muc_token(self, match_id: str) -> Response[Mapping[str, Any]]:
        """
        CoreGame_FetchAllChatMUCToken
        Get a token for all chat
        """
        r = Route(
            'GET', '/core-game/v1/matches/{match_id}/allchatmuctoken', self.region, EndpointType.glz, match_id=match_id
        )
        return self.request(r)

    def get_coregame_disassociate_player(self, match_id: str) -> Response[Mapping[str, Any]]:
        """
        CoreGame_DisassociatePlayer
        Leave an in-progress game
        """
        r = Route(
            'GET',
            '/core-game/v1/players/{puuid}/disassociate/{match_id}',
            self.region,
            EndpointType.glz,
            puuid=self.puuid,
            match_id=match_id,
        )
        return self.request(r)

    # premier endpoints

    # def get_premier_roster_(self, roster_id: str) -> Response[Any]:
    #     r = Route(
    #         'GET',
    #         '/premier/v1/rsp/rosters/v1/val-premier-{shard}/roster/{roster_id}',
    #         self.region,
    #         EndpointType.pd,
    #         shard=self.region.shard,
    #         roster_id=roster_id,
    #     )
    #     return self.request(r)

    def get_premier_eligibility(self) -> Response[premiers.Eligibility]:
        return self.request(Route('GET', '/premier/v1/player/eligibility', self.region, EndpointType.pd))

    def get_premier_conferences(self) -> Response[premiers.Conferences]:
        return self.request(
            Route(
                'GET',
                '/premier/v1/affinities/{premier_region}/conferences',
                self.region,
                EndpointType.pd,
                premier_region=self.region,
            )
        )

    @overload
    def get_premier_seasons(self, active_season: Literal[True]) -> Response[premiers.Season]: ...

    @overload
    def get_premier_seasons(self, active_season: Literal[False]) -> Response[premiers.Seasons]: ...

    @overload
    def get_premier_seasons(self, active_season: bool) -> Response[premiers.Season]: ...

    def get_premier_seasons(self, active_season: bool) -> Response[Any]:
        r = Route(
            'GET',
            '/premier/v1/affinities/{premier_region}/premier-seasons' + ('/active' if active_season else ''),
            self.region,
            EndpointType.pd,
            premier_region=self.region.shard,
        )
        return self.request(r)

    def get_premier_muc_token_proxy(self, realm: str, roster_id: str) -> Response[Any]:
        r = Route(
            'GET',
            '/premier/v1/rsp/rosters/v1/{realm}/roster/{roster_id}/muctoken',
            self.region,
            EndpointType.pd,
            realm=realm,
            roster_id=roster_id,
        )
        return self.request(r)

    def get_premier_player(self, puuid: Optional[str] = None) -> Response[premiers.Player]:
        puuid = puuid or self.puuid
        r = Route('GET', '/premier/v2/players/{puuid}', self.region, EndpointType.pd, puuid=puuid)
        return self.request(r)

    def get_premier_roster(self, roster_id: str) -> Response[Any]:
        return self.request(
            Route('GET', '/premier/v1/rosters/{roster_id}', self.region, EndpointType.pd, roster_id=roster_id)
        )

    def get_premier_roster_v2(self, roster_id: str) -> Response[Any]:
        return self.request(
            Route('GET', '/premier/v2/rosters/{roster_id}', self.region, EndpointType.pd, roster_id=roster_id)
        )

    def get_premier_roster_proxy(self, realm: str, roster_id: str) -> Response[Any]:
        r = Route(
            'GET',
            '/premier/v1/rsp/rosters/v1/{realm}/roster/{rosterId}',
            self.region,
            EndpointType.pd,
            realm=realm,
            roster_id=roster_id,
        )
        return self.request(r)

    def put_premier_set_roster_customization(
        self,
        roster_id: str,
        icon: Optional[str] = None,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        tertiary_color: Optional[str] = None,
    ) -> Response[Any]:
        """payloed example:
        {
            "icon": "iconId", // example: 6ee21acd-46ee-1a92-b0af-e98b229bdece
            "primaryColor": "(R=0.171441,G=0.003035,B=0.003035,A=1.000000)",
            "secondaryColor": "(R=0.968628,G=0.780392,B=0.000000,A=1.000000)",
            "tertiaryColor": "(R=0.090196,G=0.152941,B=0.454902,A=1.000000)"
        }
        """
        payload = {}
        if icon is not None:
            payload['icon'] = icon
        if primary_color is not None:
            payload['primaryColor'] = primary_color
        if secondary_color is not None:
            payload['secondaryColor'] = secondary_color
        if tertiary_color is not None:
            payload['tertiaryColor'] = tertiary_color
        r = Route(
            'PUT', '/premier/v1/rosters/{roster_id}/customization', self.region, EndpointType.pd, roster_id=roster_id
        )
        return self.request(r, json=payload)

    def delete_premier_roster_proxy(self, realm: str, roster_id: str) -> Response[Any]:
        r = Route(
            'DELETE',
            '/premier/v1/rsp/rosters/v1/{realm}/roster/{roster_id}',
            self.region,
            EndpointType.pd,
            realm=realm,
            roster_id=roster_id,
        )
        return self.request(r)

    def put_premier_roster_enroll(self, roster_id: str, conference_id: str) -> Response[Any]:
        payload = {'id': conference_id}
        r = Route('PUT', '/premier/v1/rosters/{roster_id}/enroll', self.region, EndpointType.pd, roster_id=roster_id)
        return self.request(r, json=payload)

    def post_premier_create_invite(self, roster_id: str, puuid: str) -> Response[Any]:
        r = Route(
            'POST',
            '/premier/v2/rosters/{roster_id}/invites/{puuid}',
            self.region,
            EndpointType.pd,
            roster_id=roster_id,
            puuid=puuid,
        )
        return self.request(r)

    def get_premier_roster_match_history(self, roster_id: str) -> Response[Any]:
        r = Route(
            'GET', '/premier/v1/rosters/{roster_id}/matchhistory', self.region, EndpointType.pd, roster_id=roster_id
        )
        return self.request(r)

    def post_premier_roster_match_history(self, roster_id: str, puuid: str) -> Response[Any]:
        r = Route(
            'POST',
            '/premier/v2/rosters/{roster_id}/invites/{puuid}/accept',
            self.region,
            EndpointType.pd,
            roster_id=roster_id,
            puuid=puuid,
        )
        payload = {}
        return self.request(r, json=payload)

    def get_premier_leaderboard_jump_to_me(
        self,
        conference: str,
        division: str,
        roster_id: str,
        season_id: str,
        page_size: Optional[int] = None,
    ) -> Response[Any]:
        """Leaderboard_JumpToMe"""
        url = 'https://euc1-red.pp.sgp.pvp.net/leaderboard/v1/name/val-premier/region/{region}/season/{season_id}/grouping/{conference}:{division}/jump-to-entry/{roster_id}'
        if page_size is not None:
            url += f'?pageSize={page_size}'
        r = Route.from_url(
            'GET',
            url=url,
            region=self.region,
            conference=conference,
            division=division,
            rosterId=roster_id,
            page_size=page_size,
            season_id=season_id,
        )
        return self.request(r)

    def get_premier_leaderboard_get_entries_by_range(
        self,
        conference: str,
        division: str,
        season_id: str,
        start_rank: int,
        end_rank: int,
    ) -> Response[Any]:
        """Leaderboard_GetEntriesByRange"""
        url = 'https://euc1-red.pp.sgp.pvp.net/leaderboard/v1/name/val-premier/region/{region}/season/{season_id}/grouping/{conference}:{division}'
        url += f'?startRank={start_rank}&endRank={end_rank}'
        r = Route.from_url(
            'GET',
            url=url,
            region=self.region,
            conference=conference,
            division=division,
            season_id=season_id,
            start_rank=start_rank,
            end_rank=end_rank,
        )
        return self.request(r)

    def post_party_make_premier_game(self, party_id: str) -> Response[Any]:
        """Party_MakePremierGame"""
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/makePremierGame',
            self.region,
            EndpointType.pd,
            party_id=party_id,
        )
        payload = {}
        return self.request(r, json=payload)

    #  https://pd.{shard}.a.pvp.net/premier/v1/rosters/{rosterId}/tournament-history
    #  https://pd.{shard}.a.pvp.net/premier/v1/tournaments/{tournamentId}/match-history

    # account-verification-player endpoints

    def post_account_verification_player_send(self) -> Response[Any]:
        ...
        # https://usw2-red.pp.sgp.pvp.net/account-verification-player/v1/sendActivationPin

    def post_account_verification_player_confirm(self) -> Response[Any]:
        ...
        # https://euc1-red.pp.sgp.pvp.net/account-verification-player/v1/confirmActivationPin

    # restrictions endpoints

    def get_restrictions_avoid_list(self) -> Response[Any]:
        r = Route('GET', '/restrictions/v1/avoidList', self.region, EndpointType.pd)
        return self.request(r)

    def post_restrictions_add_avoid_list_entry(self, puuid: Optional[str] = None) -> Response[Any]:
        puuid = puuid or self.puuid
        payload = {}
        r = Route('POST', '/restrictions/v1/avoidList/entry/{puuid}', self.region, EndpointType.pd, puuid=puuid)
        return self.request(r, json=payload)

    def delete_restrictions_remove_avoid_list_entry(self, puuid: Optional[str] = None) -> Response[Any]:
        puuid = puuid or self.puuid
        r = Route('DELETE', '/restrictions/v1/avoidList/entry/{puuid}', self.region, EndpointType.pd, puuid=puuid)
        return self.request(r)

    # tournaments endpoints

    def get_tournaments(self) -> Response[Any]:
        r = Route.from_url('GET', 'https://euc1-red.pp.sgp.pvp.net/tournaments-query/v1/product/VALORANT/tournaments')
        return self.request(r)

    def get_tournament_overview(self, tournament_id: str) -> Response[Any]:
        r = Route.from_url(
            'GET',
            'https://euc1-red.pp.sgp.pvp.net/tournaments-query/v1/product/VALORANT/tournaments/{tournament_id}/overview',
            tournament_id=tournament_id,
        )
        return self.request(r)

    # daily checkin endpoints

    def get_daily_ticket(self) -> Response[daily_ticket.DailyTicket]:
        r = Route('GET', '/daily-ticket/v1/{puuid}', self.region, EndpointType.pd, puuid=self.puuid)
        return self.request(r)

    def post_daily_ticket(self) -> Response[daily_ticket.DailyTicket]:
        r = Route('POST', '/daily-ticket/v1/{puuid}/renew', self.region, EndpointType.pd, puuid=self.puuid)
        return self.request(r)

    # esports endpoints

    def get_epsport_schedule(
        self,
        league_id: str,
        tournament_id: str,
        locale: Optional[str] = None,
    ) -> Response[esports.ScheduleLeague]:
        r = Route(
            'GET',
            '/esports-service/v1/league/{league_id}/tournament/{tournament_id}/schedule'
            + ('?locale={locale}' if locale is not None else ''),
            self.region,
            EndpointType.pd,
            league_id=league_id,
            tournament_id=tournament_id,
            locale=locale,
        )
        return self.request(r)

    def get_esport_tournament_standings(
        self,
        tournament_id: str,
        locale: Optional[str] = None,
    ) -> Response[esports.TournamentStandings]:
        # url = 'https://pd.ap.a.pvp.net/esports-service/v1/tournament/110551570691955817/standings?locale=en-US'

        r = Route(
            'GET',
            '/esports-service/v1/tournament/{tournament_id}/standings'
            + ('?locale={locale}' if locale is not None else ''),
            self.region,
            EndpointType.pd,
            tournament_id=tournament_id,
            locale=locale,
        )
        return self.request(r)

    def get_esport_teams_for_league(
        self,
        league_id: str,
        tournament_id: str,
        locale: Optional[str] = None,
    ) -> Response[esports.Teams]:
        r = Route(
            'GET',
            '/esports-service/v1/league/{league_id}/tournament/{tournament_id}/teams'
            + ('?locale={locale}' if locale is not None else ''),
            self.region,
            EndpointType.pd,
            league_id=league_id,
            tournament_id=tournament_id,
            locale=locale,
        )
        return self.request(r)

    # local endpoints

    # utils

    def __check_puuid(self, puuid: Optional[str]) -> str:
        """if puuid passed into method is None make it current user's puuid"""
        return self._puuid if puuid is None else puuid  # type: ignore

    async def __build_headers(self) -> Dict[str, Any]:
        # if self.riot_client_version is None:
        # self.riot_client_version = await self._get_current_version()
        return {
            'Authorization': 'Bearer %s' % self.riot_auth.access_token,
            'X-Riot-Entitlements-JWT': self.riot_auth.entitlements_token,
            'X-Riot-ClientPlatform': HTTPClient.RIOT_CLIENT_PLATFORM,
            'X-Riot-ClientVersion': HTTPClient.RIOT_CLIENT_VERSION,
        }

    async def _get_current_version(self) -> str:
        ...
        # resp = await self.asset_valorant_version()
        # return resp['data']['riotClientVersion']
