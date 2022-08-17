from __future__ import annotations

import asyncio
import logging
import urllib3
import aiohttp
from typing import (
    Any,
    ClassVar,
    Optional,
    # NoReturn,
    # Mapping,
    TypeVar,
    Coroutine,
    Dict,
    Union,
    TYPE_CHECKING
)
from urllib.parse import urlencode
from . import utils
from .enums import Region
from .errors import (
    HTTPException,
    Forbidden,
    NotFound,
    RiotServerError
)

MISSING = utils.MISSING

if TYPE_CHECKING:
    T = TypeVar('T')
    Response = Coroutine[Any, Any, T]

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_log = logging.getLogger(__name__)

class Route:

    BASE_URL: ClassVar[str] = "https://pd.{shard}.a.pvp.net"
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
            **parameters: Any
    ):
        self.method = method
        self.path = path
        self.endpoint = endpoint

        self.region: Optional[Region] = getattr(Region, region.upper())
        self.shard = self.region.shard

        url = ""
        if endpoint == "pd":
            url = self.BASE_URL.format(shard=self.shard) + path
        elif endpoint == "glz":
            url = self.BASE_GLZ_URL.format(region=self.region, shard=self.region) + path
        elif endpoint == "shared":
            url = self.BASE_SHARD_URL.format(shard=self.shard) + path
        elif endpoint == "play_valorant":
            url = self.BASE_PLAY_VALORANT_URL + path
        elif endpoint == "valorant_api":
            url = self.BASE_VALORANT_API_URL + path
        elif endpoint == "valtracker_gg":
            url = self.BASE_VALTRACKER_GG_URL + path

        if parameters:
            url = url + '?' + urlencode(parameters)
        self.url: str = url

class HTTPClient:

    def __init__(self) -> None:
        # self.user: Optional[ClientPlayer] = None
        self.__session: aiohttp.ClientSession = MISSING
        self.__puuid: str = MISSING
        self.__headers: Dict[str, str] = {}
        self.__client_platform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"  # noqa: E501

    async def request(self, route: Route, **kwargs: Any) -> Any:
        method = route.method
        url = route.url

        # TODO: build headers

        kwargs['headers'] = self.__headers

        exceptions = kwargs.pop('exceptions', None)

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None

        if self.__session is MISSING:
            self.__session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=0),
                # raise_for_status=True
            )

        for tries in range(5):
            try:
                async with self.__session.request(method, url, **kwargs) as response:
                    _log.debug('%s %s with %s has returned %s', method, url, kwargs.get('data'), response.status)
                    data = await utils.json_or_text(response)
                    if 300 > response.status >= 200:
                        _log.debug('%s %s has received %s', method, url, data)
                        return data

                    # if response.status == 400:
                    #     raise PhaseError(response, data)

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
                        raise RiotServerError(response, data)
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
        if self.__session:
            await self.__session.close()

    # valorant-api.com

    def asset_valorant_version(self) -> Response[Any]:
        return self.request(Route("GET", "/version", "valorant_api"))

    def asset_get_agent(self) -> Response[Any]:
        return self.request(Route('GET', '/agents', 'valorant_api', isPlayableCharacter=True, language='all'))

    def asset_get_buddy(self) -> Response[Any]:
        return self.request(Route('GET', '/buddies', 'valorant_api', language='all'))

    def asset_get_bundle(self) -> Response[Any]:
        return self.request(Route('GET', '/bundles', 'valorant_api', language='all'))

    def asset_get_ceremonie(self) -> Response[Any]:
        return self.request(Route('GET', '/ceremonies', 'valorant_api', language='all'))

    def asset_get_competitive_tier(self) -> Response[Any]:
        return self.request(Route('GET', '/competitivetiers', 'valorant_api', language='all'))

    def asset_get_content_tier(self) -> Response[Any]:
        return self.request(Route('GET', '/contenttiers', 'valorant_api', language='all'))

    def asset_get_contract(self) -> Response[Any]:
        return self.request(Route('GET', '/contracts', 'valorant_api', language='all'))

    def asset_get_currency(self) -> Response[Any]:
        return self.request(Route('GET', '/currencies', 'valorant_api', language='all'))

    def asset_get_game_mode(self) -> Response[Any]:
        return self.request(Route('GET', '/gamemodes', 'valorant_api', language='all'))

    def asset_get_gear(self) -> Response[Any]:
        return self.request(Route('GET', '/gear', 'valorant_api', language='all'))

    def asset_get_level_border(self) -> Response[Any]:
        return self.request(Route('GET', '/levelborders', 'valorant_api', language='all'))

    def asset_get_map(self) -> Response[Any]:
        return self.request(Route('GET', '/maps', 'valorant_api', language='all'))

    def asset_get_mission(self) -> Response[Any]:
        return self.request(Route('GET', '/missions', 'valorant_api', language='all'))

    def asset_get_player_card(self) -> Response[Any]:
        return self.request(Route('GET', '/playercards', 'valorant_api', language='all'))

    def asset_get_player_title(self) -> Response[Any]:
        return self.request(Route('GET', '/playertitles', 'valorant_api', language='all'))

    def asset_get_season(self) -> Response[Any]:
        return self.request(Route('GET', '/seasons', 'valorant_api', language='all'))

    def asset_get_spray(self) -> Response[Any]:
        return self.request(Route('GET', '/sprays', 'valorant_api', language='all'))

    def asset_get_theme(self) -> Response[Any]:
        return self.request(Route('GET', '/themes', 'valorant_api', language='all'))

    def asset_get_weapon(self) -> Response[Any]:
        return self.request(Route('GET', '/weapons', 'valorant_api', language='all'))

    # valtracker endpoint

    def asset_get_bundle_items(self) -> Response[Any]:
        return self.request(Route('GET', '/bundles', 'valtracker_gg'))

    # utils

    async def get_valorant_version(self) -> str:
        resp = await self.asset_valorant_version()
        return resp['data']['version']

    async def read_from_url(self, url: str) -> bytes:
        async with self.__session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise NotFound(resp, 'asset not found')
            elif resp.status == 403:
                raise Forbidden(resp, 'cannot retrieve asset')
            else:
                raise HTTPException(resp, 'failed to get asset')
