from __future__ import annotations

import asyncio
import enum
import logging
import sys
from typing import TYPE_CHECKING, Any, ClassVar, Coroutine, Dict, Optional, TypeVar, Union
from urllib.parse import quote as _uriquote

import aiohttp

from . import __version__, utils
from .errors import BadRequest, Forbidden, HTTPException, InternalServerError, NotFound, RateLimited

MISSING = utils.MISSING

if TYPE_CHECKING:
    from .types import (
        agents,
        buddies,
        bundles,
        bundles_valtracker,
        ceremonies,
        competitive_tiers,
        content_tiers,
        contracts,
        currencies,
        events,
        gamemodes,
        gear,
        level_borders,
        maps,
        missions,
        player_cards,
        player_titles,
        seasons,
        sprays,
        themes,
        version,
        weapons,
    )

    # from .types import collection, competitive, contract, match, party, player, store, version, weapons, xp

    T = TypeVar('T')
    Response = Coroutine[Any, Any, T]

_log = logging.getLogger(__name__)


# TODO: Global rate limit handling
# TODO: Global lock handling


class EndpointType(enum.Enum):
    valorant_api = 0
    valtracker_gg = 1


# http-client inspired by https://github.com/Rapptz/discord.py/blob/master/discord/http.pyS


class Route:
    BASE_VALORANT_API_URL: ClassVar[str] = 'https://valorant-api.com/v1'
    BASE_VALTRACKER_GG_URL: ClassVar[str] = 'https://api.valtracker.gg/v1'  # add-on bundle items

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

        if endpoint == EndpointType.valorant_api:
            url = self.BASE_VALORANT_API_URL + path
        elif endpoint == EndpointType.valtracker_gg:
            url = self.BASE_VALTRACKER_GG_URL + path

        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url


class HTTPClient:
    def __init__(self, session: aiohttp.ClientSession = MISSING) -> None:
        self._session: aiohttp.ClientSession = session
        user_agent = 'valorantx (https://github.com/staciax/valorantx {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

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
                        raise BadRequest(response, data)

                    # we are being rate limited
                    if response.status == 429:
                        if not response.headers.get('Via') or isinstance(data, str):
                            # Banned by Cloudflare more than likely.
                            raise HTTPException(response, data)
                        raise RateLimited(response, data)

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
        if self._session is not MISSING:
            await self._session.close()

    def clear(self) -> None:
        if self._session and self._session.closed:
            self._session = MISSING

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

    def get_agents(self, *, language: Optional[str] = 'all', is_playable_character: bool = True) -> Response[agents.Agents]:
        params = {'isPlayableCharacter': str(is_playable_character), 'language': language}
        return self.request(Route('GET', '/agents', EndpointType.valorant_api), params=params)

    def get_agent(
        self, uuid: str, *, language: Optional[str] = 'all', is_playable_character: bool = True
    ) -> Response[agents.AgentUUID]:
        params = {'isPlayableCharacter': str(is_playable_character), 'language': language}
        return self.request(Route('GET', '/agents/{uuid}', EndpointType.valorant_api, uuid=uuid), params=params)

    # -

    def get_buddies(self, *, language: Optional[str] = 'all') -> Response[buddies.Buddies]:
        return self.request(Route('GET', '/buddies', EndpointType.valorant_api), params={'language': language})

    def get_buddy(self, uuid: str, *, language: Optional[str] = 'all') -> Response[buddies.BuddyUUID]:
        return self.request(
            Route('GET', '/buddies/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    def get_buddy_levels(self, *, language: Optional[str] = 'all') -> Response[buddies.BuddyLevels]:
        return self.request(Route('GET', '/buddies/levels', EndpointType.valorant_api), params={'language': language})

    def get_buddy_level(self, uuid: str, *, language: Optional[str] = 'all') -> Response[buddies.BuddyLevelUUID]:
        return self.request(
            Route('GET', '/buddies/levels/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_bundles(self, *, language: Optional[str] = 'all') -> Response[bundles.Bundles]:
        return self.request(Route('GET', '/bundles', EndpointType.valorant_api), params={'language': language})

    def get_bundle(self, uuid: str, *, language: Optional[str] = 'all') -> Response[bundles.BundleUUID]:
        return self.request(
            Route('GET', '/bundles/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_ceremonies(self, *, language: Optional[str] = 'all') -> Response[ceremonies.Ceremonies]:
        return self.request(Route('GET', '/ceremonies', EndpointType.valorant_api), params={'language': language})

    def get_ceremony(self, uuid: str, *, language: Optional[str] = 'all') -> Response[ceremonies.CeremonyUUID]:
        return self.request(
            Route('GET', '/ceremonies/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_competitive_tiers(self, *, language: Optional[str] = 'all') -> Response[competitive_tiers.CompetitiveTiers]:
        return self.request(Route('GET', '/competitivetiers', EndpointType.valorant_api), params={'language': language})

    def get_competitive_tier(
        self, uuid: str, *, language: Optional[str] = 'all'
    ) -> Response[competitive_tiers.CompetitiveTierUUID]:
        return self.request(
            Route('GET', '/competitivetiers/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_content_tiers(self, *, language: Optional[str] = 'all') -> Response[content_tiers.ContentTiers]:
        return self.request(Route('GET', '/contenttiers', EndpointType.valorant_api), params={'language': language})

    def get_content_tier(self, uuid: str, *, language: Optional[str] = 'all') -> Response[content_tiers.ContentTierUUID]:
        return self.request(
            Route('GET', '/contenttiers/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_contracts(self, *, language: Optional[str] = 'all') -> Response[contracts.Contracts]:
        return self.request(Route('GET', '/contracts', EndpointType.valorant_api), params={'language': language})

    def get_contract(self, uuid: str, *, language: Optional[str] = 'all') -> Response[contracts.ContractUUID]:
        return self.request(
            Route('GET', '/contracts/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_currencies(self, *, language: Optional[str] = 'all') -> Response[currencies.Currencies]:
        return self.request(Route('GET', '/currencies', EndpointType.valorant_api), params={'language': language})

    def get_currency(self, uuid: str, *, language: Optional[str] = 'all') -> Response[currencies.CurrencyUUID]:
        return self.request(
            Route('GET', '/currencies/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_events(self, *, language: Optional[str] = 'all') -> Response[events.Events]:
        return self.request(Route('GET', '/events', EndpointType.valorant_api), params={'language': language})

    def get_event(self, uuid: str, *, language: Optional[str] = 'all') -> Response[events.EventUUID]:
        return self.request(
            Route('GET', '/events/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_game_modes(self, *, language: Optional[str] = 'all') -> Response[gamemodes.GameModes]:
        return self.request(Route('GET', '/gamemodes', EndpointType.valorant_api), params={'language': language})

    def get_game_mode(self, uuid: str, *, language: Optional[str] = 'all') -> Response[gamemodes.GameModeUUID]:
        return self.request(
            Route('GET', '/gamemodes/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    def get_game_mode_equippables(self, *, language: Optional[str] = 'all') -> Response[gamemodes.GameModeEquippables]:
        return self.request(Route('GET', '/gamemodes/equippables', EndpointType.valorant_api), params={'language': language})

    def get_game_mode_equippable(
        self, uuid: str, *, language: Optional[str] = 'all'
    ) -> Response[gamemodes.GameModeEquippableUUID]:
        return self.request(
            Route('GET', '/gamemodes/equippables/{uuid}', EndpointType.valorant_api, uuid=uuid),
            params={'language': language},
        )

    # -

    def get_gear(self, *, language: Optional[str] = 'all') -> Response[gear.Gear]:
        return self.request(Route('GET', '/gear', EndpointType.valorant_api), params={'language': language})

    def get_gear_(self, uuid: str, *, language: Optional[str] = 'all') -> Response[gear.GearUUID]:
        return self.request(
            Route('GET', '/gear/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_level_borders(self) -> Response[level_borders.LevelBorders]:
        return self.request(Route('GET', '/levelborders', EndpointType.valorant_api))

    def get_level_border(self, uuid: str) -> Response[level_borders.LevelBorderUUID]:
        return self.request(Route('GET', '/levelborders/{uuid}', EndpointType.valorant_api, uuid=uuid))

    # -

    def get_maps(self, *, language: Optional[str] = 'all') -> Response[maps.Maps]:
        return self.request(Route('GET', '/maps', EndpointType.valorant_api), params={'language': language})

    def get_map(self, uuid: str, *, language: Optional[str] = 'all') -> Response[maps.MapUUID]:
        return self.request(
            Route('GET', '/maps/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_missions(self, *, language: Optional[str] = 'all') -> Response[missions.Missions]:
        return self.request(Route('GET', '/missions', EndpointType.valorant_api), params={'language': language})

    def get_mission(self, uuid: str, *, language: Optional[str] = 'all') -> Response[missions.MissionUUID]:
        return self.request(
            Route('GET', '/missions/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_player_cards(self, *, language: Optional[str] = 'all') -> Response[player_cards.PlayerCards]:
        return self.request(Route('GET', '/playercards', EndpointType.valorant_api), params={'language': language})

    def get_player_card(self, uuid: str, *, language: Optional[str] = 'all') -> Response[player_cards.PlayerCardUUID]:
        return self.request(
            Route('GET', '/playercards/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_player_titles(self, *, language: Optional[str] = 'all') -> Response[player_titles.PlayerTitles]:
        return self.request(Route('GET', '/playertitles', EndpointType.valorant_api), params={'language': language})

    def get_player_title(self, uuid: str, *, language: Optional[str] = 'all') -> Response[player_titles.PlayerTitleUUID]:
        return self.request(
            Route('GET', '/playertitles/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_seasons(self, *, language: Optional[str] = 'all') -> Response[seasons.Seasons]:
        return self.request(Route('GET', '/seasons', EndpointType.valorant_api), params={'language': language})

    def get_season(self, uuid: str, *, language: Optional[str] = 'all') -> Response[seasons.SeasonUUID]:
        return self.request(
            Route('GET', '/seasons/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    def get_competitive_seasons(self) -> Response[seasons.CompetitiveSeasons]:
        return self.request(Route('GET', '/seasons/competitive', EndpointType.valorant_api))

    def get_competitive_season(self, uuid: str) -> Response[seasons.CompetitiveSeasonUUID]:
        return self.request(Route('GET', '/seasons/competitive/{uuid}', EndpointType.valorant_api, uuid=uuid))

    # -

    def get_sprays(self, *, language: Optional[str] = 'all') -> Response[sprays.Sprays]:
        return self.request(Route('GET', '/sprays', EndpointType.valorant_api), params={'language': language})

    def get_spray(self, uuid: str, *, language: Optional[str] = 'all') -> Response[sprays.SprayUUID]:
        return self.request(
            Route('GET', '/sprays/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    def get_spray_levels(self, *, language: Optional[str] = 'all') -> Response[sprays.SprayLevels]:
        return self.request(Route('GET', '/sprays/levels', EndpointType.valorant_api), params={'language': language})

    def get_spray_level(self, uuid: str, *, language: Optional[str] = 'all') -> Response[sprays.SprayLevelUUID]:
        return self.request(
            Route('GET', '/sprays/levels/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_themes(self, *, language: Optional[str] = 'all') -> Response[themes.Themes]:
        return self.request(Route('GET', '/themes', EndpointType.valorant_api), params={'language': language})

    def get_theme(self, uuid: str, *, language: Optional[str] = 'all') -> Response[themes.ThemeUUID]:
        return self.request(
            Route('GET', '/themes/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_weapons(self, *, language: Optional[str] = 'all') -> Response[weapons.Weapons]:
        return self.request(Route('GET', '/weapons', EndpointType.valorant_api), params={'language': language})

    def get_weapon(self, uuid: str, *, language: Optional[str] = 'all') -> Response[weapons.WeaponUUID]:
        return self.request(
            Route('GET', '/weapons/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    def get_weapon_skins(self, *, language: Optional[str] = 'all') -> Response[weapons.Skins]:
        return self.request(Route('GET', '/weapons/skins', EndpointType.valorant_api), params={'language': language})

    def get_weapon_skin(self, uuid: str, *, language: Optional[str] = 'all') -> Response[weapons.SkinUUID]:
        return self.request(
            Route('GET', '/weapons/skins/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    def get_weapon_skin_chromas(self, *, language: Optional[str] = 'all') -> Response[weapons.SkinChromas]:
        return self.request(Route('GET', '/weapons/skinchromas', EndpointType.valorant_api), params={'language': language})

    def get_weapon_skin_chroma(self, uuid: str, *, language: Optional[str] = 'all') -> Response[weapons.SkinChromaUUID]:
        return self.request(
            Route('GET', '/weapons/skinchromas/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    def get_weapon_skin_levels(self, *, language: Optional[str] = 'all') -> Response[weapons.SkinLevels]:
        return self.request(Route('GET', '/weapons/skinlevels', EndpointType.valorant_api), params={'language': language})

    def get_weapon_skin_level(self, uuid: str, *, language: Optional[str] = 'all') -> Response[weapons.SkinLevelUUID]:
        return self.request(
            Route('GET', '/weapons/skinlevels/{uuid}', EndpointType.valorant_api, uuid=uuid), params={'language': language}
        )

    # -

    def get_version(self) -> Response[version.Version]:
        return self.request(Route('GET', '/version', EndpointType.valorant_api))

    # valtracker endpoint

    def get_bundles_valtracker(self) -> Response[bundles_valtracker.BundlesValTracker]:
        return self.request(Route('GET', '/bundles', EndpointType.valtracker_gg))
