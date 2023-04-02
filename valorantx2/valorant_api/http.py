from __future__ import annotations

import asyncio
import enum
import logging
import sys
from typing import TYPE_CHECKING, Any, ClassVar, Coroutine, Dict, Mapping, Optional, TypeVar, Union
from urllib.parse import quote as _uriquote

import aiohttp

from .. import utils, __version__
from ..errors import Forbidden, HTTPException, InternalServerError, NotFound, PhaseError, RateLimited

try:
    import urllib3  # type: ignore
except ImportError:
    pass
else:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # type: ignore
    # disable urllib3 warnings that might arise from making requests to 127.0.0.1

MISSING = utils.MISSING

if TYPE_CHECKING:
    from .types import agent
    # from .types import collection, competitive, contract, match, party, player, store, version, weapons, xp

    T = TypeVar('T')
    Response = Coroutine[Any, Any, T]

_log = logging.getLogger(__name__)


class EndpointType(enum.Enum):
    play_valorant = 0
    valorant_api = 1
    valtracker_gg = 2

# http-client inspired by https://github.com/Rapptz/discord.py/blob/master/discord/http.pyS


class Route:
    BASE_PLAY_VALORANT_URL: ClassVar[str] = 'https://playvalorant.com'
    BASE_VALORANT_API_URL: ClassVar[str] = 'https://valorant-api.com/v1'
    BASE_VALTRACKER_GG_URL: ClassVar[str] = 'https://api.valtracker.gg/v0'  # add-on bundle items

    def __init__(
        self,
        method: str,
        path: str,
        endpoint: EndpointType = EndpointType.valorant_api,
        **parameters: Any,
    ) -> None:
        self.method = method
        self.path = path
        self.endpoint = endpoint
        self.parameters = parameters

        url = ''

        if endpoint == EndpointType.play_valorant:
            url = self.BASE_PLAY_VALORANT_URL + path
        elif endpoint == EndpointType.valorant_api:
            url = self.BASE_VALORANT_API_URL + path
        elif endpoint == EndpointType.valtracker_gg:
            url = self.BASE_VALTRACKER_GG_URL + path

        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url


class HTTPClient:
    def __init__(self, loop: asyncio.AbstractEventLoop = MISSING) -> None:
        self.loop: asyncio.AbstractEventLoop = loop
        self._session: aiohttp.ClientSession = MISSING
        self.region = ''
        user_agent = 'valorantx (https://github.com/staciax/valorantx {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    def clear(self) -> None:
        if self._session and self._session.closed:
            self._session = MISSING

    async def request(self, route: Route, **kwargs: Any) -> Any:
        method = route.method
        url = route.url
        kwargs['headers'] = {'User-Agent': self.user_agent}

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

                            return await self.request(route, asset=asset, re_authorize=False, **kwargs)
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
        if self._session is not MISSING:
            await self._session.close()

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

    # valorant-api.com

    def get_agents(self) -> Response[agent.Agent]:
        return self.request(
            Route('GET', '/agents', EndpointType.valorant_api),
            params={'isPlayableCharacter': 'True', 'language': 'all'},
            asset=True,
        )

    def get_buddies(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/buddies', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_bundles(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/bundles', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_ceremonies(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/ceremonies', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_events(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/events', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_competitive_tiers(self) -> Response[Mapping[str, Any]]:
        return self.request(
            Route('GET', '/competitivetiers', EndpointType.valorant_api), params={'language': 'all'}, asset=True
        )

    def get_content_tiers(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/contenttiers', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_contracts(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/contracts', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_currencies(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/currencies', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def asset_get_game_modes(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/gamemodes', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_game_modes_equippables(self) -> Response[Mapping[str, Any]]:
        return self.request(
            Route('GET', '/gamemodes/equippables', EndpointType.valorant_api), params={'language': 'all'}, asset=True
        )

    def get_gear(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/gear', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_level_borders(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/levelborders', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_maps(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/maps', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_missions(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/missions', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_player_cards(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/playercards', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_player_titles(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/playertitles', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_seasons(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/seasons', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_seasons_competitive(self) -> Response[Mapping[str, Any]]:
        return self.request(
            Route('GET', '/seasons/competitive', EndpointType.valorant_api), params={'language': 'all'}, asset=True
        )

    def get_sprays(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/sprays', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_themes(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/themes', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_weapons(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/weapons', EndpointType.valorant_api), params={'language': 'all'}, asset=True)

    def get_valorant_version(self) -> Response[version.Version]:
        return self.request(Route('GET', '/version', EndpointType.valorant_api), asset=True)

    # valtracker endpoint

    def get_bundles_2nd(self) -> Response[Mapping[str, Any]]:
        return self.request(Route('GET', '/bundles', EndpointType.valtracker_gg), asset=True)

    # play valorant endpoints

    def fetch_patch_notes(self, locale: str = 'en-us') -> Response[Mapping[str, Any]]:
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
