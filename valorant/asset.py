from __future__ import annotations

import os
import json
import asyncio

from functools import cache, wraps

from . import enums
from .enums import Locale, AgentID, try_enum_key
from .utils import validate_uuid

from typing import Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client
    from .enums import Locale

    UUID: Union[str, Any]

def check_validate_uuid(func):

    @wraps(func)
    def decorator(self, uuid: str = None):

        if uuid is None:
            raise func(self)

        if not validate_uuid(str(uuid)):
            raise ValueError('Invalid UUID')

        return func(self, str(uuid))

    return decorator

def try_get(enum):
    def decorator(function):
        @wraps(function)
        def wrapper(uuid):
            uuid = try_enum_key(enum, str(uuid).lower())
            return function(uuid)
        return wrapper
    return decorator

class Asset:

    asset_cache = {}

    def __init__(self, *, client: Client, locale: Union[Locale, str] = Locale.american_english) -> None:
        self._client = client
        self.locale = str(locale)
        self._reload_assets()

    @try_get(AgentID)
    @check_validate_uuid
    def get_agent(self, uuid: UUID) -> Any:
        data = self.asset_cache['agents']
        return data.get(uuid)

    @check_validate_uuid
    def get_buddy(self, uuid: UUID) -> Any:
        data = self.asset_cache['buddies']
        return data.get(uuid)

    @check_validate_uuid
    def get_bundle(self, uuid: UUID) -> Any:
        data = self.asset_cache['bundles']
        return data.get(uuid)

    @check_validate_uuid
    def get_ceremonie(self, uuid: UUID) -> Any:
        data = self.asset_cache['ceremonies']
        return data.get(uuid)

    @check_validate_uuid
    def get_competitive_tier(self, uuid: UUID) -> Any:
        data = self.asset_cache['competitive_tiers']
        return data.get(uuid)

    @check_validate_uuid
    def get_contract(self, uuid: UUID) -> Any:
        data = self.asset_cache['contracts']
        return data.get(uuid)

    @check_validate_uuid
    def get_currency(self, uuid: UUID) -> Any:
        data = self.asset_cache['currencies']
        return data.get(uuid)

    @check_validate_uuid
    def get_game_mode(self, uuid: UUID) -> Any:
        data = self.asset_cache['game_modes']
        return data.get(uuid)

    @check_validate_uuid
    def get_gear(self, uuid: UUID) -> Any:
        data = self.asset_cache['gears']
        return data.get(uuid)

    @check_validate_uuid
    def get_level_border(self, uuid: UUID) -> Any:
        data = self.asset_cache['level_borders']
        return data.get(uuid)

    @check_validate_uuid
    def get_map(self, uuid: UUID) -> Any:
        data = self.asset_cache['maps']
        return data.get(uuid)

    @check_validate_uuid
    def get_mission(self, uuid: UUID) -> Any:
        data = self.asset_cache['missions']
        return data.get(uuid)

    @check_validate_uuid
    def get_player_card(self, uuid: UUID) -> Any:
        data = self.asset_cache['player_cards']
        return data.get(uuid)

    @check_validate_uuid
    def get_player_title(self, uuid: UUID) -> Any:
        data = self.asset_cache['player_titles']
        return data.get(uuid)

    @check_validate_uuid
    def get_season(self, uuid: UUID) -> Any:
        data = self.asset_cache['seasons']
        return data.get(uuid)

    @check_validate_uuid
    def get_spray(self, uuid: UUID) -> Any:
        data = self.asset_cache['sprays']
        return data.get(uuid)

    @check_validate_uuid
    def get_theme(self, uuid: UUID) -> Any:
        data = self.asset_cache['themes']
        return data.get(uuid)

    @check_validate_uuid
    def get_weapon(self, uuid: UUID) -> Any:
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

            if filename == 'buddies.json':  # TODO: something is wrong with this one
                uuid = item['levels'][0]['uuid']
                # item['charmLevel'] = item['levels'][0]['charmLevel']
                # item['assetPath'] = item['levels'][0]['assetPath']
                # item.pop('levels')

            new_dict[uuid] = item

        Asset.asset_cache[filename[:-5]] = new_dict

    @classmethod
    def _reload_assets(cls) -> None:
        cls.asset_cache.clear()
        cls.__load_assets()
