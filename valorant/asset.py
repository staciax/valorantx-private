from __future__ import annotations

import os
import json
import asyncio

from functools import cache, wraps

from .models import (
    Agent,
    Buddy,
    Spray,
    PlayerCard,
    PlayerTitle
)

from .enums import Locale, ItemType
from .utils import validate_uuid

from typing import Any, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client
    from .enums import Locale

def check_validate_uuid(func):

    @wraps(func)
    def decorator(self, uuid: str = None):

        if uuid is None:
            raise func(self)

        if not validate_uuid(str(uuid)):
            raise ValueError('Invalid UUID')

        return func(self, str(uuid))

    return decorator

def maybe_uuid(key: str = 'displayName'):

    def decorator(function):

        @wraps(function)
        def wrapper(self, uuid: str = None):

            if uuid is None:
                raise function(self)

            if not validate_uuid(str(uuid)):

                get_key = function.__doc__.split(',')[0].strip()
                data = self.asset_cache[get_key]

                for value in data.values():
                    display_name = value.get(key)
                    if display_name is not None:
                        for name in display_name.values():
                            if name.lower().startswith(uuid.lower()) or uuid.lower() == name.lower():
                                return function(self, value['uuid'])

                raise ValueError('Invalid UUID')

            return function(self, str(uuid))
        return wrapper
    return decorator

class Asset:

    asset_cache = {}

    def __init__(self, *, client: Client, locale: Union[Locale, str] = Locale.american_english) -> None:
        self._client = client
        self.locale = str(locale)
        self._reload_assets()

    @maybe_uuid()
    def get_agent(self, uuid: str) -> Optional[Agent]:
        """ agents, Get an agent by UUID. """
        agents = self.asset_cache['agents']
        data = agents.get(uuid)
        return Agent(client=self._client, data=data) if data is not None else None

    @maybe_uuid()
    def get_buddy(self, uuid: str) -> Optional[Buddy]:
        """ buddies, Get a buddy by UUID. """
        buddies = self.asset_cache['buddies']
        data = buddies.get(uuid)
        return Buddy(client=self._client, data=data) if data else None

    @maybe_uuid()
    def get_bundle(self, uuid: str) -> Any:
        """ bundles, Get a bundle by UUID. """
        bundles = self.asset_cache['bundles']
        data = bundles.get(uuid)
        return data.get(uuid)

    @check_validate_uuid
    def get_ceremonie(self, uuid: str) -> Any:
        data = self.asset_cache['ceremonies']
        return data.get(uuid)

    @check_validate_uuid
    def get_competitive_tier(self, uuid: str) -> Any:
        data = self.asset_cache['competitive_tiers']
        return data.get(uuid)

    @check_validate_uuid
    def get_contract(self, uuid: str) -> Any:
        data = self.asset_cache['contracts']
        return data.get(uuid)

    @check_validate_uuid
    def get_currency(self, uuid: str) -> Any:
        data = self.asset_cache['currencies']
        return data.get(uuid)

    @check_validate_uuid
    def get_game_mode(self, uuid: str) -> Any:
        data = self.asset_cache['game_modes']
        return data.get(uuid)

    @check_validate_uuid
    def get_gear(self, uuid: str) -> Any:
        data = self.asset_cache['gears']
        return data.get(uuid)

    @check_validate_uuid
    def get_level_border(self, uuid: str) -> Any:
        data = self.asset_cache['level_borders']
        return data.get(uuid)

    @check_validate_uuid
    def get_map(self, uuid: str) -> Any:
        data = self.asset_cache['maps']
        return data.get(uuid)

    @check_validate_uuid
    def get_mission(self, uuid: str) -> Any:
        data = self.asset_cache['missions']
        return data.get(uuid)

    @maybe_uuid()
    def get_player_card(self, uuid: str) -> Optional[PlayerCard]:
        """ player_cards, Get a player card by UUID. """
        player_cards = self.asset_cache['player_cards']
        data = player_cards.get(uuid)
        return PlayerCard(client=self._client, data=data) if data else None

    @maybe_uuid()
    def get_player_title(self, uuid: str) -> Optional[PlayerTitle]:
        """ player_titles, Get a player title by UUID. """
        player_titles = self.asset_cache['player_titles']
        data = player_titles.get(uuid)
        return PlayerTitle(client=self._client, data=data) if data else None

    @check_validate_uuid
    def get_season(self, uuid: str) -> Any:
        data = self.asset_cache['seasons']
        return data.get(uuid)

    @maybe_uuid()
    def get_spray(self, uuid: str) -> Optional[Spray]:
        """ sprays, Get a spray by UUID. """
        sprays = self.asset_cache['sprays']
        data = sprays.get(uuid)
        return Spray(client=self._client, data=data) if data else None

    @check_validate_uuid
    def get_theme(self, uuid: str) -> Any:
        data = self.asset_cache['themes']
        return data.get(uuid)

    @check_validate_uuid
    def get_weapon(self, uuid: str) -> Any:
        data = self.asset_cache['weapons']
        return data.get(uuid)

    async def fetch_all_assets(self) -> None:

        get_version = await self._client.http.get_valorant_version()
        if get_version != self._client.version:
            self._client.version = get_version

        async_tasks = [
            asyncio.ensure_future(self._client.http.asset_get_agent()),
            asyncio.ensure_future(self._client.http.asset_get_buddy()),
            asyncio.ensure_future(self._client.http.asset_get_bundle()),
            asyncio.ensure_future(self._client.http.asset_get_ceremonie()),
            asyncio.ensure_future(self._client.http.asset_get_competitive_tier()),
            asyncio.ensure_future(self._client.http.asset_get_contract()),
            asyncio.ensure_future(self._client.http.asset_get_currency()),
            asyncio.ensure_future(self._client.http.asset_get_game_mode()),
            asyncio.ensure_future(self._client.http.asset_get_gear()),
            asyncio.ensure_future(self._client.http.asset_get_level_border()),
            asyncio.ensure_future(self._client.http.asset_get_map()),
            asyncio.ensure_future(self._client.http.asset_get_mission()),
            asyncio.ensure_future(self._client.http.asset_get_player_card()),
            asyncio.ensure_future(self._client.http.asset_get_player_title()),
            asyncio.ensure_future(self._client.http.asset_get_season()),
            asyncio.ensure_future(self._client.http.asset_get_spray()),
            asyncio.ensure_future(self._client.http.asset_get_theme()),
            asyncio.ensure_future(self._client.http.asset_get_weapon()),

            # bundle items
            asyncio.ensure_future(self._client.http.asset_get_bundle_items()),
        ]
        assets = await asyncio.gather(*async_tasks)
        for index, asset in enumerate(assets, start=1):
            if index == 1:
                self.__dump_to(asset, 'agents')
            elif index == 2:
                self.__dump_to(asset, 'buddies')
            elif index == 3:
                self.__dump_to(asset, 'bundles')
            elif index == 4:
                self.__dump_to(asset, 'ceremonies')
            elif index == 5:
                self.__dump_to(asset, 'competitive_tiers')
            elif index == 6:
                self.__dump_to(asset, 'contracts')
            elif index == 7:
                self.__dump_to(asset, 'currencies')
            elif index == 8:
                self.__dump_to(asset, 'game_modes')
            elif index == 9:
                self.__dump_to(asset, 'gears')
            elif index == 10:
                self.__dump_to(asset, 'level_borders')
            elif index == 11:
                self.__dump_to(asset, 'maps')
            elif index == 12:
                self.__dump_to(asset, 'missions')
            elif index == 13:
                self.__dump_to(asset, 'player_cards')
            elif index == 14:
                self.__dump_to(asset, 'player_titles')
            elif index == 15:
                self.__dump_to(asset, 'seasons')
            elif index == 16:
                self.__dump_to(asset, 'sprays')
            elif index == 17:
                self.__dump_to(asset, 'themes')
            elif index == 18:
                self.__dump_to(asset, 'weapons')
            elif index == 19:
                self.__dump_to(asset, '_bundle_items')
            else:
                print(f"Unknown asset type: {index}")

    @staticmethod
    @cache
    def __path() -> str:
        return os.path.join(os.path.dirname(__file__), 'data')

    def __dump_to(self, data: Any, filename: str) -> None:
        with open(os.path.join(self.__path(), f"{filename}.json"), "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @classmethod
    def __load_assets(cls) -> None:
        path = cls.__path()
        for filename in os.listdir(path):
            if filename.endswith('.json'):
                cls.__to_cache(path, filename)

    @classmethod
    def __to_cache(cls, path: str, filename: str) -> None:
        with open(os.path.join(path, filename), encoding='utf-8') as f:
            to_dict = json.load(f)
            cls.__customize_asset_cache_format(filename, to_dict)

    @staticmethod
    def __customize_asset_cache_format(filename: str, data: Any) -> None:

        new_dict = {}
        for item in data['data']:
            uuid = item['uuid']

            if filename.startswith('buddies'):
                uuid = item['levels'][0]['uuid']
                item['uuid'] = uuid
                item['charmLevel'] = item['levels'][0]['charmLevel']
                item['assetPath'] = item['levels'][0]['assetPath']
                item.pop('levels')

            elif filename.startswith('sprays'):
                uuid = item['levels'][0]['uuid']
                item['uuid'] = uuid
                item['sprayLevel'] = item['levels'][0]['sprayLevel']
                item['assetPath'] = item['levels'][0]['assetPath']
                item.pop('levels')

            elif filename.startswith('_bundle_items'):
                bundle = Asset.asset_cache['bundles'][uuid]
                bundle['price'] = item['price']
                bundle_items = []
                default_payload = dict(amount=1, discount=0)
                for weapon in item['weapons']:
                    bundle_items.append(dict(
                        uuid=weapon['levels'][0]['uuid'],
                        type=str(ItemType.skin),
                        price=weapon.get('price', 0),
                        **default_payload
                    ))
                for buddy in item['buddies']:
                    bundle_items.append(dict(
                        uuid=buddy['levels'][0]['uuid'],
                        type=str(ItemType.buddy),
                        price=buddy.get('price', 0),
                        **default_payload
                    ))
                for card in item['cards']:
                    bundle_items.append(dict(
                        uuid=card['uuid'],
                        type=str(ItemType.player_card),
                        price=card.get('price', 0),
                        **default_payload
                    ))
                for spray in item['sprays']:
                    bundle_items.append(dict(
                        uuid=spray['uuid'],
                        type=str(ItemType.spray),
                        price=spray.get('price', 0),
                        **default_payload
                    ))
                bundle['items'] = bundle_items

            new_dict[uuid] = item

        Asset.asset_cache[filename[:-5]] = new_dict

    @classmethod
    def _reload_assets(cls) -> None:
        cls.asset_cache.clear()
        cls.__load_assets()
