from __future__ import annotations

import asyncio
import enum
import logging
from typing import TYPE_CHECKING, Any, ClassVar, Coroutine, Dict, List, Mapping, NoReturn, Optional, TypeVar, Union
from urllib.parse import quote as _uriquote

import aiohttp

from . import __version__, utils
from .auth import RiotAuth
from .enums import ItemType, Locale, QueueType, Region, try_enum
from .errors import Forbidden, HTTPException, InternalServerError, NotFound, PhaseError, RateLimited

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
    # from .types import collection, competitive, contract, match, party, player, store, version, weapons, xp

    T = TypeVar('T')
    Response = Coroutine[Any, Any, T]

_log = logging.getLogger(__name__)


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
        endpoint: EndpointType = EndpointType.pd,
        region: Region = Region.AP,
        **parameters: Any,
    ) -> None:
        self.method = method
        self.path = path
        self.endpoint = endpoint
        self.region: Region = region
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


class HTTPClient:
    def __init__(self, loop: asyncio.AbstractEventLoop = MISSING) -> None:
        self.loop: asyncio.AbstractEventLoop = loop
        # self.user: Optional[ClientPlayer] = None
        self._session: aiohttp.ClientSession = MISSING
        self._headers: Dict[str, Any] = {}
        self._client_platform = 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9'  # noqa: E501
        self._riot_auth: RiotAuth = RiotAuth()
        self._puuid: str = self._riot_auth.puuid
        self._region: Region = try_enum(Region, self._riot_auth.region, Region.AP)
        self._riot_client_version: str = ''

    @property
    def region(self) -> Region:
        return self._region

    @region.setter
    def region(self, region: Region) -> None:
        self._region = region

    @property
    def puuid(self) -> str:
        return self._puuid

    @puuid.setter
    def puuid(self, puuid: str) -> None:
        self._puuid = puuid

    def clear(self) -> None:
        if self._session and self._session.closed:
            self._session = MISSING

    async def request(self, route: Route, **kwargs: Any) -> Any:
        method = route.method
        url = route.url
        re_authorize = kwargs.pop('re_authorize', True)
        extra_exceptions = kwargs.pop('exceptions', None)
        kwargs['headers'] = self._headers

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
                            await self.__build_headers()
                            re_authorize = False
                            continue
                        raise PhaseError(response, data)

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
                        if extra_exceptions is not None:
                            raise NotFound(response, extra_exceptions)
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

    async def static_login(self, username: str, password: str) -> RiotAuth:
        """Riot Auth login."""
        await self._riot_auth.authorize(username, password)
        self._puuid = self._riot_auth.puuid
        await self.__build_headers()
        if self._session is MISSING:
            self._session = aiohttp.ClientSession()
        return self._riot_auth

    async def token_login(self, data: Dict[str, Any]) -> RiotAuth:
        """Riot Auth login."""

        self._riot_auth.from_data(data)
        self._puuid = self._riot_auth.puuid
        await self.__build_headers()
        if self._session is MISSING:
            self._session = aiohttp.ClientSession()
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

    # play valorant endpoints

    def fetch_patch_notes(self, locale: Union[str, Locale] = Locale.american_english) -> Response[Mapping[str, Any]]:
        """
        FetchPatchNote
        Get the latest patch note
        """
        r = Route(
            'GET',
            '/page-data/{locale}/news/tags/patch-notes/page-data.json',
            EndpointType.play_valorant,
            self.region,
            locale=str(locale).lower(),
        )
        return self.request(r)

    # PVP endpoints

    def fetch_content(self) -> Response[Mapping[str, Any]]:
        """
        Content_FetchContent
        Get names and ids for game content such as agents, maps, guns, etc.
        """
        return self.request(Route('GET', '/content-service/v3/content', EndpointType.shard, self.region))

    def fetch_account_xp(self) -> Response[xp.AccountXP]:
        """
        AccountXP_GetPlayer
        Get the account level, XP, and XP history for the active player
        """
        return self.request(Route('GET', '/account-xp/v1/players/{puuid}', EndpointType.pd, self.region, puuid=self.puuid))

    def fetch_player_loadout(self) -> Response[collection.Loadout]:
        """
        playerLoadoutUpdate
        Get the player's current loadout
        """
        return self.request(
            Route(
                'GET',
                '/personalization/v2/players/{puuid}/playerloadout',
                EndpointType.pd,
                self.region,
                puuid=self.puuid,
            )
        )

    def put_player_loadout(self, loadout: Mapping) -> Response[collection.Loadout]:
        """
        playerLoadoutUpdate
        Use the values from self._fetch_player_loadout() excluding properties like subject and version.
        Loadout changes take effect when starting a new game
        """
        r = Route(
            'PUT',
            '/personalization/v2/players/{puuid}/playerloadout',
            EndpointType.pd,
            self.region,
            puuid=self.puuid,
        )
        return self.request(r, json=loadout)

    def fetch_mmr(self, puuid: Optional[str] = None) -> Response[competitive.MatchmakingRating]:
        """
        MMR_FetchPlayer
        Get the match making rating for a player
        """
        puuid = self.__check_puuid(puuid)
        return self.request(Route('GET', '/mmr/v1/players/{puuid}', EndpointType.pd, self.region, puuid=puuid))

    def fetch_match_history(
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

        r = Route('GET', '/match-history/v1/history/{puuid}', EndpointType.pd, self._region, puuid=puuid)
        params = {
            'startIndex': start_index,
            'endIndex': end_index,
        }
        if queue_id is not None:
            params['queue'] = queue_id  # type: ignore
        return self.request(r, params=params)

    def fetch_match_details(self, match_id: str) -> Response[match.MatchDetails]:
        """
        Get the full info for a previous match
        Includes everything that the in-game match details screen shows including damage and kill positions,
        same as the official API w/ a production key
        """
        return self.request(
            Route(
                'GET',
                '/match-details/v1/matches/{match_id}',
                EndpointType.pd,
                self.region,
                match_id=match_id,
            )
        )

    def fetch_competitive_updates(
        self,
        puuid: Optional[str] = None,
        start_index: int = 0,
        end_index: int = 15,
        queue_id: Union[str, QueueType] = QueueType.competitive,
    ) -> Response[Mapping[str, Any]]:
        """
        MMR_FetchCompetitiveUpdates
        Get recent games and how they changed ranking
        There are 3 optional query parameters: start_index, end_index, and queue_id. queue can be one of null,
        competitive, custom, deathmatch, ggteam, newmap, onefa, snowball, spikerush, or unrated.
        """
        puuid = self.__check_puuid(puuid)
        if isinstance(queue_id, QueueType):
            queue_id = str(queue_id)
        r = Route('GET', '/mmr/v1/players/{puuid}/competitiveupdates', EndpointType.pd, region=self._region, puuid=puuid)
        params = {'startIndex': start_index, 'endIndex': end_index}
        if queue_id is not None:
            params['queue'] = queue_id  # type: ignore

        return self.request(r, params=params)

    def fetch_leaderboard(
        self,
        season_id: Optional[str],
        start_index: int = 0,
        size: int = 25,
        region: Union[str, Region] = Region.AP,
    ) -> Response[Mapping[str, Any]]:
        """
        MMR_FetchLeaderboard
        Get the competitive leaderboard for a given season
        The query parameter query can be added to search for a username.
        """
        if season_id is None:
            raise ValueError('Season cannot be empty')

        region = try_enum(Region, region, Region.AP)

        r = Route(
            'GET',
            '/mmr/v1/leaderboards/affinity/{l_region}/queue/competitive/season/{season}',
            EndpointType.pd,
            region=self._region,
            l_region=str(region),
            season=season_id,
        )
        params = {'startIndex': start_index, 'size': size}

        return self.request(r, params=params)

    def fetch_player_restrictions(self) -> Response[Mapping[str, Any]]:
        """
        Restrictions_FetchPlayerRestrictionsV3
        Checks for any gameplay penalties on the account
        """
        return self.request(Route('GET', '/restrictions/v3/penalties', EndpointType.pd, self.region))

    def fetch_item_progression_definitions(self) -> Response[Mapping[str, Any]]:
        """
        ItemProgressionDefinitionsV2_Fetch
        Get details for item upgrades
        """
        return self.request(Route('GET', '/contract-definitions/v3/item-upgrades', EndpointType.pd, self.region))

    def fetch_config(self) -> Response[Mapping[str, Any]]:
        """
        Config_FetchConfig
        Get various internal game configuration settings set by Riot
        """
        return self.request(Route('GET', '/v1/config/{region}', EndpointType.shard, self.region))

    def fetch_name_by_puuid(self, puuid: Optional[Union[List[str], str]] = None) -> Response[List[player.NameService]]:
        """
        Name_service
        get player name tag by puuid
        NOTE:
        format ['PUUID']
        """
        if puuid is None:
            puuid = []

        if isinstance(puuid, str):
            puuid = [puuid]

        return self.request(Route('PUT', '/name-service/v2/players', EndpointType.pd, self.region), json=puuid)

    # contract endpoints

    def contract_fetch_definitions(self) -> Response[Mapping[str, Any]]:
        """
        ContractDefinitions_Fetch
        Get names and descriptions for contracts
        """
        return self.request(Route('GET', '/contract-definitions/v3/definitions', EndpointType.pd, self.region))

    def contracts_fetch(self) -> Response[contract.Contracts]:
        """
        Contracts_Fetch
        Get a list of contracts and completion status including match history
        """
        return self.request(Route('GET', '/contracts/v1/contracts/{puuid}', EndpointType.pd, self.region, puuid=self.puuid))

    def contracts_activate(self, contract_id: str) -> Response[contract.Contracts]:
        """
        Contracts_Activate
        Activate a particular contract

        {contract id}: The ID of the contract to activate. Can be found from the ContractDefinitions_Fetch endpoint.
        """
        r = Route(
            'POST',
            '/contracts/v1/contracts/{puuid}/special/{contract}',
            EndpointType.pd,
            self.region,
            puuid=self.puuid,
            contract=contract_id,
        )
        return self.request(r)

    def contracts_fetch_active_story(self) -> Response[Mapping[str, Any]]:
        """
        ContractDefinitions_FetchActiveStory
        Get the battlepass contracts
        """
        return self.request(Route('GET', '/contract-definitions/v2/definitions/story', EndpointType.pd, self.region))

    def item_progress_fetch_definitions(self) -> Response[Mapping[str, Any]]:
        """
        ItemProgressDefinitionsV2_Fetch
        Fetch definitions for skin upgrade progressions
        """
        return self.request(Route('GET', '/contract-definitions/v3/item-upgrades', EndpointType.pd, self.region))

    def contracts_unlock_item_progress(self, progression_id: str) -> Response[Mapping[str, Any]]:
        """
        Contracts_UnlockItemProgressV2
        Unlock an item progression
        """
        return self.request(
            Route(
                'POST',
                '/contracts/v2/item-upgrades/{progression}/{puuid}',
                EndpointType.pd,
                self.region,
                puuid=self.puuid,
                progression=progression_id,
            )
        )

    # store endpoints

    def store_fetch_offers(self) -> Response[store.Offers]:
        """
        Store_GetOffers
        Get prices for all store items
        """
        return self.request(Route('GET', '/store/v1/offers/', EndpointType.pd, self.region))

    def store_fetch_storefront(self) -> Response[store.StoreFront]:
        """
        Store_GetStorefrontV2
        Get the currently available items in the store
        """
        return self.request(Route('GET', '/store/v2/storefront/{puuid}', EndpointType.pd, self.region, puuid=self.puuid))

    def store_fetch_wallet(self) -> Response[store.Wallet]:
        """
        Store_GetWallet
        Get amount of Valorant points and Radianite the player has
        Valorant points have the id 85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741
        and Radianite points have the id e59aa87c-4cbf-517a-5983-6e81511be9b7
        """
        return self.request(Route('GET', '/store/v1/wallet/{puuid}', EndpointType.pd, self.region, puuid=self.puuid))

    def store_fetch_order(self, order_id: str) -> Response[Mapping[str, Any]]:
        """
        Store_GetOrder
        {order id}: The ID of the order. Can be obtained when creating an order.
        """
        return self.request(Route('GET', '/store/v1/order/{order}', EndpointType.pd, self.region, order=order_id))

    def store_fetch_entitlements(
        self, item_type: Optional[Union[str, ItemType]] = None
    ) -> Response[store.EntitlementsByTypes]:
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
            '/store/v1/entitlements/{puuid}' + ('/{item_type}'.format(item_type=item_type) if item_type is not None else ''),
            EndpointType.pd,
            region=self._region,
            puuid=self.puuid,
        )
        return self.request(r)

    # party endpoints

    # party endpoints

    def party_fetch_player(self) -> Response[party.PartyPlayer]:
        """
        Party_FetchPlayer
        Get the Party ID that a given player belongs to
        """
        return self.request(Route('GET', '/parties/v1/players/{puuid}', EndpointType.glz, self.region, puuid=self.puuid))

    def party_remove_player(self, puuid: str) -> Response[NoReturn]:
        """
        Party_RemovePlayer
        Removes a player from the current party
        """
        puuid = self.__check_puuid(puuid)
        return self.request(Route('DELETE', '/parties/v1/players/{puuid}', EndpointType.glz, self.region, puuid=puuid))

    def fetch_party(self, party_id: str) -> Response[party.Party]:
        """
        Party_FetchParty
        Get details about a given party id
        """
        r = Route('GET', '/parties/v1/parties/{party_id}', EndpointType.glz, self.region, party_id=party_id)
        return self.request(r)

    def party_set_member_ready(self, party_id: str, ready: bool) -> Response[Mapping[str, Any]]:
        """
        Party_SetMemberReady
        Sets whether a party member is ready for queueing or not
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/setReady',
            EndpointType.glz,
            self.region,
            party_id=party_id,
            puuid=self.puuid,
        )
        payload = {'ready': ready}
        return self.request(r, json=payload)

    def party_refresh_competitive_tier(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_RefreshCompetitiveTier
        Refreshes the competitive tier for a player
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/refreshCompetitiveTier',
            EndpointType.glz,
            region=self._region,
            party_id=party_id,
            puuid=self.puuid,
        )
        return self.request(r)

    def party_refresh_player_identity(self, party_id: str) -> Response[party.Party]:
        """
        Party_RefreshPlayerIdentity
        Refreshes the identity for a player
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/refreshPlayerIdentity',
            EndpointType.glz,
            region=self._region,
            party_id=party_id,
            puuid=self.puuid,
        )
        return self.request(r)

    def party_refresh_pings(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_RefreshPings
        Refreshes the pings for a player
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/refreshPings',
            EndpointType.glz,
            region=self._region,
            party_id=party_id,
            puuid=self.puuid,
        )
        return self.request(r)

    def party_change_queue(self, party_id: str, queue_id: Union[QueueType, str]) -> Response[party.Party]:
        """
        Party_ChangeQueue
        Sets the matchmaking queue for the party
        """
        r = Route('POST', '/parties/v1/parties/{party_id}/queue', EndpointType.glz, self.region, party_id=party_id)
        payload = {'queueID': str(queue_id)}
        return self.request(r, json=payload)

    def party_start_custom_game(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_StartCustomGame
        Starts a custom game
        """
        r = Route('POST', '/parties/v1/parties/{party_id}/startcustomgame', EndpointType.glz, self.region, party_id=party_id)
        return self.request(r)

    def party_enter_matchmaking_queue(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_EnterMatchmakingQueue
        Enters the matchmaking queue
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/matchmaking/join',
            EndpointType.glz,
            self.region,
            party_id=party_id,
        )
        return self.request(r)

    def party_leave_matchmaking_queue(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_LeaveMatchmakingQueue
        Leaves the matchmaking queue
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/matchmaking/leave',
            EndpointType.glz,
            self.region,
            party_id=party_id,
        )
        return self.request(r)

    def set_party_accessibility(self, party_id: str, open_join: bool) -> Response[party.Party]:
        """
        Party_SetAccessibility
        Changes the party accessibility to be open or closed
        """
        r = Route('POST', '/parties/v1/parties/{party_id}/accessibility', EndpointType.glz, self.region, party_id=party_id)
        payload = {"accessibility": ("OPEN" if open_join else "CLOSED")}
        return self.request(r, json=payload)

    def party_set_custom_game_settings(self, party_id: str, settings: Mapping) -> Response[Mapping[str, Any]]:
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
            EndpointType.glz,
            self.region,
            party_id=party_id,
        )
        return self.request(r, json=settings)

    def party_invite_by_display_name(self, party_id: str, name: str, tag: str) -> Response[Mapping[str, Any]]:
        """
        Party_InviteToPartyByDisplayName
        Invites a player to the party with their display name
        omit the "#" in tag
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/invites/name/{name}/tag/{tag}',
            EndpointType.glz,
            self.region,
            party_id=party_id,
            name=name,
            tag=tag,
        )
        return self.request(r)

    def party_request_to_join(self, party_id: str, other_puuid: str) -> Response[Mapping[str, Any]]:
        """
        Party_RequestToJoinParty
        Requests to join a party
        """
        r = Route('POST', '/parties/v1/parties/{party_id}/request', EndpointType.glz, self.region, party_id=party_id)
        payload = {'Subjects': [other_puuid]}
        return self.request(r, json=payload)

    def party_decline_request(self, party_id: str, request_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_DeclineRequest
        Declines a party request
        {request id}: The ID of the party request. Can be found from the Requests array on the Party_FetchParty endpoint.
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/request/{request_id}/decline',
            EndpointType.glz,
            self.region,
            party_id=party_id,
            request_id=request_id,
        )
        return self.request(r)

    def party_join(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_PlayerJoin
        Join a party
        """
        r = Route(
            'POST',
            '/parties/v1/players/{puuid}/joinparty/{party_id}',
            EndpointType.glz,
            self.region,
            puuid=self.puuid,
            party_id=party_id,
        )
        return self.request(r)

    def party_leave(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_PlayerLeave
        Leave a party
        """
        r = Route(
            'POST',
            '/parties/v1/players/{puuid}/leaveparty/{party_id}',
            EndpointType.glz,
            self.region,
            puuid=self.puuid,
            party_id=party_id,
        )
        return self.request(r)

    def party_fetch_custom_game_configs(self) -> Response[Mapping[str, Any]]:
        """
        Party_FetchCustomGameConfigs
        Get information about the available game modes
        """
        r = Route('GET', f'/parties/v1/parties/customgameconfigs', EndpointType.glz, self.region)
        return self.request(r)

    def party_fetch_muc_token(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_FetchMUCToken
        Get a token for party chat
        """
        r = Route('GET', '/parties/v1/parties/{party_id}/muctoken', EndpointType.glz, self.region, party_id=party_id)
        return self.request(r)

    def party_fetch_voice_token(self, party_id: str) -> Response[Mapping[str, Any]]:
        """
        Party_FetchVoiceToken
        Get a token for party voice
        """
        r = Route('GET', '/parties/v1/parties/{party_id}/voicetoken', EndpointType.glz, self.region, party_id=party_id)
        return self.request(r)

    def party_transfer_owner(self, party_id: str, puuid: str) -> Response[Mapping[str, Any]]:
        """
        Party_TransferOwner
        Transfer party ownership
        """
        r = Route(
            'POST',
            '/parties/v1/parties/{party_id}/members/{puuid}/owner',
            EndpointType.glz,
            self.region,
            party_id=party_id,
            puuid=puuid,
        )
        return self.request(r)

    def party_leave_from_party(self, party_id: str, puuid: str) -> Response[Mapping[str, Any]]:
        """
        Party_LeaveFromParty
        Kick a player from the party
        """
        r = Route(
            'DELETE',
            '/parties/v1/parties/{party_id}/members/{puuid}',
            EndpointType.glz,
            self.region,
            party_id=party_id,
            puuid=puuid,
        )
        return self.request(r)

    # queue endpoints

    def queue_matchmaking_fetch_queue(self) -> Response[Mapping[str, Any]]:
        """
        QueueMatchmaking_FetchQueue
        Get information about the current queue
        """
        r = Route('GET', f'/matchmaking/v1/queues/configs ', EndpointType.glz, self.region)
        return self.request(r)

    # favorite endpoints

    def favorites_fetch(self) -> Response[weapons.Favorites]:
        """
        FetchFavorite
        Get the favorite list of the authenticated user
        """
        r = Route('GET', '/favorites/v1/players/{puuid}/favorites', EndpointType.pd, self.region, puuid=self.puuid)
        return self.request(r)

    def favorite_post(self, item_id: str) -> Response[weapons.Favorites]:
        """
        PostFavorite
        Add a player to the favorite list of the authenticated user
        """
        r = Route('POST', '/favorites/v1/players/{puuid}/favorites', EndpointType.pd, self.region, puuid=self.puuid)
        payload = {'ItemID': item_id}
        return self.request(r, json=payload)

    def favorite_delete(self, item_id: str) -> Response[weapons.Favorites]:
        """
        DeleteFavorite
        Remove a player from the favorite list of the authenticated user
        """
        item_id_without_dashes = str(item_id).replace('-', '')
        r = Route(
            'DELETE',
            '/favorites/v1/players/{puuid}/favorites/{item_id}',
            EndpointType.pd,
            region=self._region,
            puuid=self.puuid,
            item_id=item_id_without_dashes,
        )
        return self.request(r)

    # pre game endpoints
    # exceptions = {404: [PhaseError, "You are not in a pre-game"]},

    def pregame_fetch_player(self) -> Response[Mapping[str, Any]]:
        """
        Pregame_GetPlayer
        Get the ID of a game in the pre-game stage
        """
        r = Route('GET', '/pregame/v1/players/{puuid}', EndpointType.glz, self.region, puuid=self.puuid)
        return self.request(r)

    def pregame_fetch_match(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        Pregame_GetMatch
        Get info for a game in the pre-game stage
        """
        r = Route('GET', '/pregame/v1/matches/{match_id}', EndpointType.glz, self.region, match_id=match_id)
        return self.request(r)

    def pregame_fetch_match_loadouts(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        Pregame_GetMatchLoadouts
        Get player skins and sprays for a game in the pre-game stage
        """
        r = Route('GET', '/pregame/v1/matches/{match_id}/loadouts', EndpointType.glz, self.region, match_id=match_id)
        return self.request(r)

    def pregame_fetch_chat_token(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        Pregame_FetchChatToken
        Get a chat token
        """
        r = Route('GET', '/pregame/v1/matches/{match_id}/chattoken', EndpointType.glz, self.region, match_id=match_id)
        return self.request(r)

    def pregame_fetch_voice_token(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        Pregame_FetchVoiceToken
        Get a voice token
        """
        r = Route('GET', '/pregame/v1/matches/{match_id}/voicetoken', EndpointType.glz, self.region, match_id=match_id)
        return self.request(r)

    def pregame_select_character(self, agent_id: str, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        Pregame_SelectCharacter
        Select an agent
        don't use this for instalocking :)
        """
        r = Route(
            'POST',
            '/pregame/v1/matches/{match_id}/select/{agent_id}',
            EndpointType.glz,
            self.region,
            match_id=match_id,
            agent_id=agent_id,
        )
        return self.request(r)

    def pregame_lock_character(self, agent_id: str, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        Pregame_LockCharacter
        Lock in an agent
        don't use this for instalocking :)
        """
        r = Route(
            'POST',
            '/pregame/v1/matches/{match_id}/lock/{agent_id}',
            EndpointType.glz,
            self.region,
            match_id=match_id,
            agent_id=agent_id,
        )
        return self.request(r)

    def pregame_quit_match(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        Pregame_QuitMatch
        Quit a match in the pre-game stage
        """
        r = Route('POST', '/pregame/v1/matches/{match_id}/quit', EndpointType.glz, self.region, match_id=match_id)
        return self.request(r)

    # live game endpoints
    # exceptions={404: [PhaseError, "You are not in a core-game"]},

    def coregame_fetch_player(self) -> Response[Mapping[str, Any]]:
        """
        CoreGame_FetchPlayer
        Get the game ID for an ongoing game the player is in
        """
        r = Route('GET', '/core-game/v1/players/{puuid}', EndpointType.glz, self.region, puuid=self.puuid)
        return self.request(r)

    def coregame_fetch_match(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        CoreGame_FetchMatch
        Get information about an ongoing game
        """
        r = Route('GET', '/core-game/v1/matches/{match_id}', EndpointType.glz, self.region, match_id=match_id)
        return self.request(r)

    def coregame_fetch_match_loadouts(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        CoreGame_FetchMatchLoadouts
        Get player skins and sprays for an ongoing game
        """
        r = Route('GET', '/core-game/v1/matches/{match_id}/loadouts', EndpointType.glz, self.region, match_id=match_id)
        return self.request(r)

    def coregame_fetch_team_chat_muc_token(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        CoreGame_FetchTeamChatMUCToken
        Get a token for team chat
        """
        r = Route(
            'GET', '/core-game/v1/matches/{match_id}/teamchatmuctoken', EndpointType.glz, self.region, match_id=match_id
        )
        return self.request(r)

    def coregame_fetch_all_chat_muc_token(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        CoreGame_FetchAllChatMUCToken
        Get a token for all chat
        """
        r = Route(
            'GET', '/core-game/v1/matches/{match_id}/allchatmuctoken', EndpointType.glz, self.region, match_id=match_id
        )
        return self.request(r)

    def coregame_disassociate_player(self, match_id: Optional[str] = None) -> Response[Mapping[str, Any]]:
        """
        CoreGame_DisassociatePlayer
        Leave an in-progress game
        """
        r = Route(
            'GET',
            '/core-game/v1/players/{puuid}/disassociate/{match_id}',
            EndpointType.glz,
            self.region,
            puuid=self.puuid,
            match_id=match_id,
        )
        return self.request(r)

    # local endpoints

    # utils

    def __check_puuid(self, puuid: Optional[str]) -> str:
        """if puuid passed into method is None make it current user's puuid"""
        return self._puuid if puuid is None else puuid

    async def __build_headers(self) -> None:
        if self._riot_client_version == '':
            self._riot_client_version = await self._get_current_version()

        self._headers['Authorization'] = f'Bearer %s' % self._riot_auth.access_token
        self._headers['X-Riot-Entitlements-JWT'] = self._riot_auth.entitlements_token
        self._headers['X-Riot-ClientPlatform'] = self._client_platform
        self._headers['X-Riot-ClientVersion'] = self._riot_client_version

    async def _get_current_version(self) -> str:
        ...
        # resp = await self.asset_valorant_version()
        # return resp['data']['riotClientVersion']
