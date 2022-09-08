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
import sys
from typing import TYPE_CHECKING, Any, ClassVar, Coroutine, Dict, List, Mapping, Optional, TypeVar, Union  # NoReturn,
from urllib.parse import urlencode

import aiohttp
import urllib3

from . import __version__, utils
from .auth import RiotAuth
from .enums import ItemType, Locale, QueueID, Region, try_enum
from .errors import Forbidden, HTTPException, NotFound, RiotServerError, ValorantAPIServerError

MISSING = utils.MISSING

if TYPE_CHECKING:
    T = TypeVar('T')
    Response = Coroutine[Any, Any, T]
    from .types import collection, contract, match, player, store, version, xp


# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_log = logging.getLogger(__name__)


class Route:

    BASE_PD_URL: ClassVar[str] = "https://pd.{shard}.a.pvp.net"
    BASE_GLZ_URL: ClassVar[str] = "https://glz-{region}-1.{shard}.a.pvp.net"
    BASE_SHARD_URL: ClassVar[str] = "https://shared.{shard}.a.pvp.net"
    BASE_PLAY_VALORANT_URL: ClassVar[str] = "https://playvalorant.com"
    BASE_VALORANT_API_URL: ClassVar[str] = "https://valorant-api.com/v1"
    BASE_VALTRACKER_GG_URL: ClassVar[str] = "https://api.valtracker.gg"  # add-on bundle items

    def __init__(
        self,
        method: str,
        path: str,
        endpoint: Optional[str] = "pd",
        region: str = "ap",
        **parameters: Any,
    ) -> None:
        self.method = method
        self.path = path
        self.endpoint = endpoint
        self.region: Optional[Region] = getattr(Region, region.upper())
        self.parameters = parameters

        self.shard = self.region.shard

        url = ''

        if endpoint == 'pd':
            url = self.BASE_PD_URL.format(shard=self.shard) + path
        elif endpoint == 'glz':
            url = self.BASE_GLZ_URL.format(region=self.region, shard=self.region) + path
        elif endpoint == 'shared':
            url = self.BASE_SHARD_URL.format(shard=self.shard) + path
        elif endpoint == 'play_valorant':
            url = self.BASE_PLAY_VALORANT_URL + path
        elif endpoint == 'valorant_api':
            url = self.BASE_VALORANT_API_URL + path
        elif endpoint == 'valtracker_gg':
            url = self.BASE_VALTRACKER_GG_URL + path

        if parameters:
            url = url + '?' + urlencode(parameters)
        self.url: str = url


class HTTPClient:
    def __init__(self) -> None:
        # self.user: Optional[ClientPlayer] = None
        self._session: aiohttp.ClientSession = MISSING
        self._headers: Dict[str, str] = {}
        self._client_platform = 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'  # noqa: E501
        self._riot_auth: RiotAuth = RiotAuth()
        self._puuid: str = self._riot_auth.user_id
        self._riot_client_version: str = ''

        user_agent = 'valorantx (https://github.com/staciax/valorantx {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def request(self, route: Route, asset_endpoint: bool = False, re_authorize: bool = True, **kwargs: Any) -> Any:
        method = route.method
        url = route.url

        if not asset_endpoint:
            kwargs['headers'] = self._headers
        else:
            kwargs['headers'] = {
                'User-Agent': self.user_agent,
            }

        exceptions = kwargs.pop('exceptions', None)

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
                    data = await utils.json_or_text(response)
                    if 300 > response.status >= 200:
                        _log.debug('%s %s has received %s', method, url, data)
                        return data

                    if response.status == 400:
                        if re_authorize:
                            await self._riot_auth.reauthorize()
                            await self.request(route, asset_endpoint, False, **kwargs)
                        # raise PhaseError(response, data)

                    # we are being rate limited
                    if response.status == 429:
                        if not response.headers.get('Via') or isinstance(data, str):
                            # Banned by Cloudflare more than likely.
                            raise HTTPException(response, data)

                    if response.status in {500, 502, 504, 524}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    if response.status == 403:
                        raise Forbidden(response, data)
                    elif response.status == 404:
                        if exceptions is not None:
                            raise NotFound(response, exceptions)
                        raise NotFound(response, data)
                    elif response.status >= 500:
                        if not asset_endpoint:
                            raise RiotServerError(response, data)
                        else:
                            raise ValorantAPIServerError(response, data)
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
                raise RiotServerError(response, data)

            raise HTTPException(response, data)

        raise RuntimeError('Unreachable code in HTTP handling')

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def static_login(self, username: str, password: str) -> RiotAuth:
        """Riot Auth login."""
        await self._riot_auth.authorize(username, password)
        self._puuid = self._riot_auth.puuid
        await self.__build_headers()
        return self._riot_auth

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

    # valorant-api.com

    def asset_valorant_version(self) -> Response[version.Version]:
        return self.request(Route("GET", "/version", "valorant_api"), asset_endpoint=True)

    def asset_get_agents(self) -> Response[Any]:
        r = Route('GET', '/agents', 'valorant_api', isPlayableCharacter=True, language='all')
        return self.request(r, asset_endpoint=True)

    def asset_get_buddies(self) -> Response[Any]:
        return self.request(Route('GET', '/buddies', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_bundles(self) -> Response[Any]:
        return self.request(Route('GET', '/bundles', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_ceremonies(self) -> Response[Any]:
        return self.request(Route('GET', '/ceremonies', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_events(self) -> Response[Any]:
        return self.request(Route('GET', '/events', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_competitive_tiers(self) -> Response[Any]:
        return self.request(Route('GET', '/competitivetiers', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_content_tiers(self) -> Response[Any]:
        return self.request(Route('GET', '/contenttiers', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_contracts(self) -> Response[Any]:
        return self.request(Route('GET', '/contracts', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_currencies(self) -> Response[Any]:
        return self.request(Route('GET', '/currencies', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_game_modes(self) -> Response[Any]:
        return self.request(Route('GET', '/gamemodes', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_game_modes_equippables(self) -> Response[Any]:
        return self.request(Route('GET', '/gamemodes/equippables', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_gear(self) -> Response[Any]:
        return self.request(Route('GET', '/gear', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_level_borders(self) -> Response[Any]:
        return self.request(Route('GET', '/levelborders', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_maps(self) -> Response[Any]:
        return self.request(Route('GET', '/maps', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_missions(self) -> Response[Any]:
        return self.request(Route('GET', '/missions', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_player_cards(self) -> Response[Any]:
        return self.request(Route('GET', '/playercards', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_player_titles(self) -> Response[Any]:
        return self.request(Route('GET', '/playertitles', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_seasons(self) -> Response[Any]:
        return self.request(Route('GET', '/seasons', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_seasons_competitive(self) -> Response[Any]:
        return self.request(Route('GET', '/seasons/competitive', 'valorant_api'), asset_endpoint=True)

    def asset_get_sprays(self) -> Response[Any]:
        return self.request(Route('GET', '/sprays', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_themes(self) -> Response[Any]:
        return self.request(Route('GET', '/themes', 'valorant_api', language='all'), asset_endpoint=True)

    def asset_get_weapons(self) -> Response[Any]:
        return self.request(Route('GET', '/weapons', 'valorant_api', language='all'), asset_endpoint=True)

    # valtracker endpoint

    def asset_get_bundle_items(self) -> Response[Any]:
        return self.request(Route('GET', '/bundles', 'valtracker_gg'), asset_endpoint=True)

    # play valorant endpoints

    def fetch_patch_notes(self, locale: Union[str, Locale] = Locale.american_english) -> Response[None]:
        """
        FetchPatchNote
        Get the latest patch note
        """
        r = Route("GET", f"/page-data/{str(locale).lower()}/news/tags/patch-notes/page-data.json", "play_valorant")
        return self.request(r)

    # PVP endpoints

    def fetch_content(self) -> Response[Any]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        return self.request(Route('GET', '/content-service/v3/content', 'shared'))

    def fetch_account_xp(self) -> Response[xp.AccountXP]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        return self.request(Route('GET', f'/account-xp/v1/players/{self._puuid}', 'pd'))

    def fetch_player_loadout(self) -> Response[collection.Loadout]:
        """
        playerLoadoutUpdate
        Get the player's current loadout
        """
        return self.request(Route('GET', f'/personalization/v2/players/{self._puuid}/playerloadout', 'pd'))

    def put_player_loadout(self, loadout: Mapping) -> Response[collection.Loadout]:
        """
        playerLoadoutUpdate
        Use the values from self._fetch_player_loadout() excluding properties like subject and version.
        Loadout changes take effect when starting a new game
        """
        r = Route('PUT', f'/personalization/v2/players/{self._puuid}/playerloadout', 'pd')
        return self.request(r, json=loadout)

    def fetch_mmr(self, puuid: Optional[str] = None) -> Response[Any]:
        """
        MMR_FetchPlayer
        Get the match making rating for a player
        """
        puuid = self.__check_puuid(puuid)
        return self.request(Route('GET', f'/mmr/v1/players/{puuid}', 'pd'))

    def fetch_match_history(
        self,
        puuid: Optional[str] = None,
        start_index: int = 0,
        end_index: int = 15,
        queue_id: Union[str, QueueID] = QueueID.unrated,
    ) -> Response[match.MatchHistory]:
        """
        MatchHistory_FetchMatchHistory
        Get recent matches for a player
        There are 3 optional query parameters: start_index, end_index, and queue_id.queue can be one of null,
        competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        """

        puuid = self.__check_puuid(puuid)
        if isinstance(queue_id, str):
            queue_id = try_enum(QueueID, queue_id, QueueID.unrated)
        r = Route(
            'GET',
            f'/match-history/v1/history/{puuid}',
            'pd',
            startIndex=start_index,
            endIndex=end_index,
            queue=str(queue_id),
        )
        return self.request(r)

    def fetch_match_details(self, match_id: str) -> Response[match.MatchDetails]:
        """
        Get the full info for a previous match
        Includes everything that the in-game match details screen shows including damage and kill positions,
        same as the official API w/ a production key
        """
        return self.request(Route("GET", f"/match-details/v1/matches/{match_id}", "pd"))

    def fetch_competitive_updates(
        self,
        puuid: Optional[str] = None,
        start_index: int = 0,
        end_index: int = 15,
        queue_id: Union[str, QueueID] = QueueID.competitive,
    ) -> Response[Any]:
        """
        MMR_FetchCompetitiveUpdates
        Get recent games and how they changed ranking
        There are 3 optional query parameters: start_index, end_index, and queue_id. queue can be one of null,
        competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        """
        queue_id = try_enum(QueueID, queue_id, QueueID.competitive)
        puuid = self.__check_puuid(puuid)
        r = Route(
            "GET",
            f"/mmr/v1/players/{puuid}/competitiveupdates",
            "pd",
            startIndex=start_index,
            endIndex=end_index,
            queue=str(queue_id),
        )
        return self.request(r)

    def fetch_leaderboard(
        self,
        season: str,
        start_index: int = 0,
        size: int = 25,
        region: Union[str, Region] = Region.AP,
    ) -> Response[None]:
        """
        MMR_FetchLeaderboard
        Get the competitive leaderboard for a given season
        The query parameter query can be added to search for a username.
        """
        if season == '':
            season = self.__get_live_season()  # TODO: fix this

        region = try_enum(Region, region, Region.AP)

        r = Route(
            'GET',
            f'/mmr/v1/leaderboards/affinity/{str(region)}/queue/competitive/season/{season}',
            'pd',
            startIndex=start_index,
            size=size,
        )
        return self.request(r)

    def fetch_player_restrictions(self) -> Response[Any]:
        """
        Restrictions_FetchPlayerRestrictionsV3
        Checks for any gameplay penalties on the account
        """
        return self.request(Route('GET', '/restrictions/v3/penalties', 'pd'))

    def fetch_item_progression_definitions(self) -> Response[Any]:
        """
        ItemProgressionDefinitionsV2_Fetch
        Get details for item upgrades
        """
        return self.request(Route('GET', '/contract-definitions/v3/item-upgrades', 'pd'))

    def fetch_config(self) -> Response[None]:
        """
        Config_FetchConfig
        Get various internal game configuration settings set by Riot
        """
        return self.request(Route('GET', '/v1/config/{region}', 'shared'))

    def fetch_name_by_puuid(self, puuid: Optional[List[str]] = None) -> Response[Any]:
        """
        Name_service
        get player name tag by puuid
        NOTE:
        format ['PUUID']
        """
        if puuid is None:
            puuid = []
        return self.request(Route('PUT', '/name-service/v2/players', 'pd'), json=puuid)

    # contract endpoints

    def contract_fetch_definitions(self) -> Response[Any]:
        """
        ContractDefinitions_Fetch
        Get names and descriptions for contracts
        """
        return self.request(Route('GET', '/contract-definitions/v3/definitions', 'pd'))

    def contracts_fetch(self) -> Response[contract.Contracts]:
        """
        Contracts_Fetch
        Get a list of contracts and completion status including match history
        """
        return self.request(Route('GET', f'/contracts/v1/contracts/{self._puuid}', 'pd'))

    def contracts_activate(self, contract_id: str) -> Response[Any]:
        """
        Contracts_Activate
        Activate a particular contract

        {contract id}: The ID of the contract to activate. Can be found from the ContractDefinitions_Fetch endpoint.
        """
        r = Route('POST', f'/contracts/v1/contracts/{self._puuid}/special/{contract_id}', 'pd')
        return self.request(r)

    def contracts_fetch_active_story(self) -> Response[Any]:
        """
        ContractDefinitions_FetchActiveStory
        Get the battlepass contracts
        """
        return self.request(Route('GET', '/contract-definitions/v2/definitions/story', 'pd'))

    def item_progress_fetch_definitions(self) -> Response[Any]:
        """
        ItemProgressDefinitionsV2_Fetch
        Fetch definitions for skin upgrade progressions
        """
        return self.request(Route('GET', '/contract-definitions/v3/item-upgrades', 'pd'))

    def contracts_unlock_item_progress(self, progression_id: str) -> Response[Any]:
        """
        Contracts_UnlockItemProgressV2
        Unlock an item progression
        """
        return self.request(Route('POST', f'/contracts/v2/item-upgrades/{progression_id}/{self._puuid}', 'pd'))

    # store endpoints

    def store_fetch_offers(self) -> Response[store.Offers]:
        """
        Store_GetOffers
        Get prices for all store items
        """
        return self.request(Route('GET', '/store/v1/offers/', 'pd'))

    def store_fetch_storefront(self) -> Response[store.StoreFront]:
        """
        Store_GetStorefrontV2
        Get the currently available items in the store
        """
        return self.request(Route('GET', f'/store/v2/storefront/{self._puuid}', 'pd'))

    def store_fetch_wallet(self) -> Response[store.Wallet]:
        """
        Store_GetWallet
        Get amount of Valorant points and Radianite the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741
        and Radianite points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7
        """
        return self.request(Route('GET', f'/store/v1/wallet/{self._puuid}', 'pd'))

    def store_fetch_order(self, order_id: str) -> Response[Any]:
        """
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        """
        return self.request(Route('GET', f'/store/v1/order/{order_id}', 'pd'))

    def store_fetch_entitlements(self, item_type: Union[str, ItemType] = ItemType.skin) -> Response[Any]:
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
        r = Route('GET', f'/store/v1/entitlements/{self._puuid}/{str(item_type)}', 'pd')
        return self.request(r)

    # utils

    # local utility functions

    # def __get_live_season(self) -> str:
    #     """Get the UUID of the live competitive season"""
    # content = self.fetch_content()
    # season_id = [season["ID"] for season in content["Seasons"] if season["IsActive"] and season["Type"] == "act"]
    #     if not season_id:
    #         return self.fetch_player_mmr()["LatestCompetitiveUpdate"]["SeasonID"]
    #     return season_id[0]

    # def __check_party_id(self, party_id: str) -> str:
    #     """If party ID passed into method is None make it user's current party"""
    #     return self.__get_current_party_id() if party_id is None else party_id

    # def __get_current_party_id(self) -> str:
    #     """Get the user's current party ID"""
    #     party = self.party_fetch_player()
    #     return party["CurrentPartyID"]

    # def __coregame_check_match_id(self, match_id: str) -> str:
    # """Check if a match id was passed into the method"""
    # return self.coregame_fetch_player()["MatchID"] if match_id is None else match_id

    # def __pregame_check_match_id(self, match_id: str) -> str:
    #     return self.pregame_fetch_player()["MatchID"] if match_id is None else match_id

    def __check_puuid(self, puuid: str) -> str:
        """If puuid passed into method is None make it current user's puuid"""
        return self._puuid if puuid is None else puuid

    async def __build_headers(self) -> None:

        if self._riot_client_version == '':
            self._riot_client_version = await self._get_current_version()

        self._headers['Authorization'] = f"Bearer %s" % self._riot_auth.access_token
        self._headers['X-Riot-Entitlements-JWT'] = self._riot_auth.entitlements_token
        self._headers['X-Riot-ClientPlatform'] = self._client_platform
        self._headers['X-Riot-ClientVersion'] = self._riot_client_version

    async def _get_current_version(self) -> str:
        resp = await self.asset_valorant_version()
        return resp['data']['riotClientVersion']
