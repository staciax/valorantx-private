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
import json
import logging
import os
import shutil
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Mapping, Optional, TypeVar, Union
from typing_extensions import ParamSpec, Concatenate

from .enums import CurrencyID, ItemType
from .errors import AuthRequired
from .utils import is_uuid

if TYPE_CHECKING:
    from .client import Client

# fmt: off
__all__ = (
    'Assets',
)
# fmt: on

P = ParamSpec('P')
R = TypeVar('R')

_log = logging.getLogger(__name__)


def _find(value: Any, key: Any) -> bool:
    if isinstance(value, list) and isinstance(key, list):
        return key in value
    elif isinstance(value, str) and isinstance(key, str):
        value = value.lower()
        key = key.lower()
        return value == key
    elif isinstance(value, int) and isinstance(key, int):
        return value == key
    elif isinstance(value, float) and isinstance(key, float):
        return value == key
    elif isinstance(value, bool) and isinstance(key, bool):
        return value == key
    elif isinstance(value, str) and isinstance(key, dict):
        for key_value in key.values():
            if _find(value, key_value):
                return True
    elif isinstance(value, dict) and isinstance(key, str):
        for value_value in value.values():
            if _find(value_value, key):
                return True
    elif isinstance(value, dict) and isinstance(key, dict):
        for key_value in key.values():
            if _find(value, key_value):
                return True
    elif isinstance(value, list) and isinstance(key, str):
        for list_value in value:
            if _find(list_value, key):
                return True
    else:
        return False


def _finder():
    def decorator(function: Callable[Concatenate[Assets, P], R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(self: Assets, *args: ParamSpec.args, **kwargs: ParamSpec.kwargs) -> Any:

            if not args and not kwargs:
                return function(self, uuid=None)

            new_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(key, str):
                    key = key.lower()
                if isinstance(value, str):
                    value = value.lower()
                new_kwargs[key] = value

            kwargs = new_kwargs

            finder_keys = [x for x in list(kwargs.keys())]
            # inspired by https://github.com/MinshuG/valorant-api/blob/b739850d2722247b56b9e4d12caa8b3c326ce141/valorant_api/base_list.py#L17  # noqa: E501

            get_key = function.__doc__.split(',')[0].strip()
            data = Assets.ASSET_CACHE.get(get_key, {})

            if not data:
                return function(self, *args, **kwargs)

            is_level_border = True
            if len(finder_keys) == 0:
                may_be_uuid = args[0]
                if isinstance(may_be_uuid, str):
                    may_be_uuid = may_be_uuid.lower()

                if not is_uuid(str(may_be_uuid)) and not may_be_uuid == '':
                    if isinstance(may_be_uuid, int):
                        if get_key == 'level_borders':
                            kwargs['startinglevel'] = may_be_uuid
                            finder_keys.append('startinglevel')
                            is_level_border = True

            maybe = []
            for key, value in data.items():

                if isinstance(value, dict):
                    for k, v in value.items():

                        if isinstance(k, str):
                            k = k.lower()

                        if k in finder_keys:

                            if isinstance(v, str):
                                if _find(v, kwargs[k]):
                                    return function(self, key)
                                elif v.startswith(kwargs[k]):
                                    maybe.append(key)

                            elif isinstance(v, int):

                                if is_level_border:
                                    next_level = v + 19

                                    if kwargs[k] > 20:
                                        next_level += 1

                                    if kwargs[k] < next_level:
                                        return function(self, key)

                                else:
                                    if _find(v, kwargs[k]):
                                        return function(self, key)

                            elif isinstance(v, dict):
                                for kk, vv in v.items():
                                    if _find(vv, kwargs[k]):
                                        return function(self, key)
                                    elif vv.startswith(kwargs[k]):
                                        maybe.append(key)

                            # EN: Not tested yet
                            elif isinstance(v, list):
                                for vv in v:
                                    if isinstance(vv, str):
                                        if _find(vv, kwargs[k]):
                                            return function(self, key)
                                        elif vv.startswith(kwargs[k]):
                                            maybe.append(key)

                        else:
                            for arg in args:
                                if isinstance(arg, str):
                                    arg = arg.lower()
                                if isinstance(key, str):
                                    key = key.lower()
                                if arg == key:
                                    return function(self, key)

            # 2nd loop
            for key, value in data.items():
                if isinstance(value, dict):
                    for v_ in value.values():
                        for arg in args:
                            if _find(v_, arg):
                                return function(self, key)

                            if isinstance(value, dict):
                                for v_find in value.values():
                                    if isinstance(v_find, dict):
                                        for vv_find in v_find.values():
                                            if isinstance(vv_find, str) and isinstance(arg, str):
                                                vv_find = vv_find.lower()
                                                arg = arg.lower()
                                                if vv_find.startswith(arg):
                                                    maybe.append(key)

            # 1st choice in maybe
            if len(maybe) > 0:
                return function(self, maybe[0])
            return function(self, uuid=None)

        return wrapper

    return decorator


class Assets:

    _cache_dir: Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    ASSET_CACHE = {}
    OFFER_CACHE = {}

    def __init__(self, *, client: Client, auto_reload: bool) -> None:
        self._client = client
        if auto_reload:
            self.reload_assets()

    @staticmethod
    def clear_asset_cache() -> None:
        Assets.ASSET_CACHE.clear()

    @staticmethod
    def clear_offer_cache() -> None:
        Assets.OFFER_CACHE.clear()

    @staticmethod
    def clear_all_cache() -> None:
        Assets.clear_asset_cache()
        Assets.clear_offer_cache()

    def get_asset(self, key: str, tries: int = 3) -> Optional[Dict[str, Any]]:
        """Get an asset."""
        if key in self.ASSET_CACHE:
            return self.ASSET_CACHE[key]

        for _ in range(tries):
            try:
                if key in self.ASSET_CACHE:
                    return self.ASSET_CACHE[key]
                else:
                    _log.warning(f'Asset {key} not found')
                    raise KeyError(f"Asset {key!r} not found")
            except KeyError:
                self.reload_assets()
                if _ >= tries - 1:
                    raise KeyError(f"Asset {key!r} not found")

    @_finder()
    def get_agent(self, uuid: str) -> Optional[Dict[str, Any]]:
        """agents, Get an agent by UUID."""
        data = self.get_asset('agents')
        return data.get(uuid)

    @_finder()
    def get_buddy(self, uuid: str) -> Optional[Dict[str, Any]]:
        """buddies, Get a buddy by UUID."""
        data = self.get_asset('buddies')
        return data.get(uuid)

    @_finder()
    def get_buddy_level(self, uuid: str) -> Optional[Dict[str, Any]]:
        """buddies_levels, Get a buddy level by UUID."""
        data = self.get_asset('buddies_levels')
        return data.get(uuid)

    @_finder()
    def get_bundle(self, uuid: str) -> Optional[Dict[str, Any]]:
        """bundles, Get a bundle by UUID."""
        data = self.get_asset('bundles')
        return data.get(uuid)

    @_finder()
    def get_ceremony(self, uuid: str) -> Optional[Dict[str, Any]]:
        """ceremonies, Get a ceremony by UUID."""
        data = self.get_asset('ceremonies')
        return data.get(uuid)

    @_finder()
    def get_competitive_tier(self, uuid: str) -> Optional[Dict[str, Any]]:
        """competitive_tiers, Get a competitive tier by UUID."""
        data = self.get_asset('competitive_tiers')
        return data.get(uuid)

    @_finder()
    def get_content_tier(self, uuid: str) -> Optional[Dict[str, Any]]:
        """content_tiers, Get a content tier by UUID."""
        data = self.get_asset('content_tiers')
        return data.get(uuid)

    @_finder()
    def get_contract(self, uuid: str) -> Optional[Dict[str, Any]]:
        """contracts, Get a contract by UUID."""
        data = self.get_asset('contracts')
        return data.get(uuid)

    @_finder()
    def get_currency(self, uuid: str) -> Optional[Dict[str, Any]]:
        """currencies, Get a currency by UUID."""
        data = self.get_asset('currencies')
        return data.get(uuid)

    @_finder()
    def get_event(self, uuid: str) -> Optional[Dict[str, Any]]:
        """events, Get an event by UUID."""
        data = self.get_asset('events')
        return data.get(uuid)

    @_finder()
    def get_game_mode(self, uuid: str) -> Optional[Dict[str, Any]]:
        """game_modes, Get a game mode by UUID."""
        data = self.get_asset('game_modes')
        return data.get(uuid)

    @_finder()
    def get_game_mode_equippable(self, uuid: str) -> Optional[Dict[str, Any]]:
        """game_modes_equippables, Get a game mode equippable by UUID."""
        data = self.get_asset('game_modes_equippables')
        return data.get(uuid)

    @_finder()
    def get_gear(self, uuid: str) -> Optional[Dict[str, Any]]:
        """gear, Get a gear by UUID."""
        data = self.get_asset('gear')
        return data.get(uuid)

    @_finder()
    def get_level_border(self, uuid: str) -> Optional[Dict[str, Any]]:
        """level_borders, Get a level border by UUID."""
        data = self.get_asset('level_borders')
        return data.get(uuid)

    @_finder()
    def get_map(self, uuid: str) -> Optional[Dict[str, Any]]:
        """maps, Get a map by UUID."""
        data = self.get_asset('maps')
        return data.get(uuid)

    @_finder()
    def get_mission(self, uuid: str) -> Optional[Dict[str, Any]]:
        """missions, Get a mission by UUID."""
        data = self.get_asset('missions')
        return data.get(uuid)

    @_finder()
    def get_player_card(self, uuid: str) -> Optional[Dict[str, Any]]:
        """player_cards, Get a player card by UUID."""
        data = self.get_asset('player_cards')
        return data.get(uuid)

    @_finder()
    def get_player_title(self, uuid: str) -> Optional[Dict[str, Any]]:
        """player_titles, Get a player title by UUID."""
        data = self.get_asset('player_titles')
        return data.get(uuid)

    @_finder()
    def get_season(self, uuid: str) -> Optional[Dict[str, Any]]:
        """seasons, Get a season by UUID."""
        data = self.get_asset('seasons')
        return data.get(uuid)

    @_finder()
    def get_season_competitive(self, uuid: str) -> Optional[Dict[str, Any]]:
        """seasons_competitive, Get a season competitive by UUID."""
        data = self.get_asset('seasons_competitive')
        return data.get(uuid)

    @_finder()
    def get_spray(self, uuid: str) -> Optional[Dict[str, Any]]:
        """sprays, Get a spray by UUID."""
        data = self.get_asset('sprays')
        return data.get(uuid)

    @_finder()
    def get_spray_level(self, uuid: str) -> Optional[Dict[str, Any]]:
        """sprays_levels, Get a spray level by UUID."""
        data = self.get_asset('sprays_levels')
        return data.get(uuid)

    @_finder()
    def get_theme(self, uuid: str) -> Optional[Dict[str, Any]]:
        """themes, Get a theme by UUID."""
        data = self.get_asset('themes')
        return data.get(uuid)

    @_finder()
    def get_weapon(self, uuid: str) -> Optional[Dict[str, Any]]:
        """weapons, Get a weapon by UUID."""
        data = self.get_asset('weapons')
        return data.get(uuid)

    @_finder()
    def get_skin(self, uuid: str) -> Optional[Dict[str, Any]]:
        """weapon_skins, Get a weapon skin by UUID."""
        data = self.get_asset('weapon_skins')
        return data.get(uuid)

    @_finder()
    def get_skin_level(self, uuid: str) -> Optional[Dict[str, Any]]:
        """weapon_skins_levels, Get a weapon skin level by UUID."""
        data = self.get_asset('weapon_skins_levels')
        return data.get(uuid)

    @_finder()
    def get_skin_chroma(self, uuid: str) -> Optional[Dict[str, Any]]:
        """weapon_skins_chromas, Get a weapon skin chroma by UUID."""
        data = self.get_asset('weapon_skins_chromas')
        return data.get(uuid)

    def get_item_price(self, uuid: str) -> int:
        return self.OFFER_CACHE.get(uuid, 0)

    async def fetch_assets(
        self,
        *,
        force: bool = False,
        with_price: bool = False,
        reload_asset: bool = False,
    ) -> None:
        """Fetch all assets."""

        get_version = await self._client.get_valorant_version()

        if get_version != self._client.version:
            self._client.version = get_version

        self.__mkdir_assets_dir()
        asset_path = self._get_asset_dir()

        file_list = (  # TODO: something...
            'agents',
            'buddies',
            'bundles',
            'ceremonies',
            'currencies',
            'competitive_tiers',
            'content_tiers',
            'contracts',
            'currencies',
            'events',
            'game_modes',
            'game_modes_equippables',
            'gear',
            'level_borders',
            'maps',
            'missions',
            'player_cards',
            'player_titles',
            'seasons',
            'seasons_competitive',
            'sprays',
            'themes',
            'weapons',
            '_bundle_items',
        )

        # verify files exist

        list_dir = os.listdir(asset_path)
        for filename in file_list:
            if (filename + '.json') not in list_dir:
                force = True
                if len(list_dir) > 0:
                    _log.warning('some assets are missing, forcing update')
                break

        # fetch offer/price of items

        if with_price:
            if not self._client.is_authorized():
                raise AuthRequired("You need to be authorized to fetch prices")
            if 'offers.json' not in list_dir:
                data = await self._client.fetch_offers()
                new_dict = {}
                for offer in data.offers:
                    new_dict[offer.id] = offer.cost
                self._dump(new_dict, '_offers')
        else:
            if self._client.is_authorized():
                if not self.OFFER_CACHE:
                    _log.info('You can fetch items prices by calling `client.fetch_offers(with_price=True)`')
            else:
                _log.info('Skipping fetching items prices')

        if not asset_path.endswith(get_version.version) or len(os.listdir(self._get_asset_dir())) == 0 or force:
            _log.info(f"Fetching assets for version {get_version.version!r}")

            async_tasks = [
                asyncio.ensure_future(self._client.http.asset_get_agents()),
                asyncio.ensure_future(self._client.http.asset_get_buddies()),
                asyncio.ensure_future(self._client.http.asset_get_bundles()),
                asyncio.ensure_future(self._client.http.asset_get_ceremonies()),
                asyncio.ensure_future(self._client.http.asset_get_competitive_tiers()),
                asyncio.ensure_future(self._client.http.asset_get_content_tiers()),
                asyncio.ensure_future(self._client.http.asset_get_contracts()),
                asyncio.ensure_future(self._client.http.asset_get_currencies()),
                asyncio.ensure_future(self._client.http.asset_get_events()),
                asyncio.ensure_future(self._client.http.asset_get_game_modes()),
                asyncio.ensure_future(self._client.http.asset_get_game_modes_equippables()),
                asyncio.ensure_future(self._client.http.asset_get_gear()),
                asyncio.ensure_future(self._client.http.asset_get_level_borders()),
                asyncio.ensure_future(self._client.http.asset_get_maps()),
                asyncio.ensure_future(self._client.http.asset_get_missions()),
                asyncio.ensure_future(self._client.http.asset_get_player_cards()),
                asyncio.ensure_future(self._client.http.asset_get_player_titles()),
                asyncio.ensure_future(self._client.http.asset_get_seasons()),
                asyncio.ensure_future(self._client.http.asset_get_seasons_competitive()),
                asyncio.ensure_future(self._client.http.asset_get_sprays()),
                asyncio.ensure_future(self._client.http.asset_get_themes()),
                asyncio.ensure_future(self._client.http.asset_get_weapons()),
                # bundle items
                asyncio.ensure_future(self._client.http.asset_get_bundle_items()),
            ]
            assets = await asyncio.gather(*async_tasks)
            for index, asset in enumerate(assets, start=1):
                if index == 1:
                    self._dump(asset, 'agents')
                elif index == 2:
                    self._dump(asset, 'buddies')
                elif index == 3:
                    self._dump(asset, 'bundles')
                elif index == 4:
                    self._dump(asset, 'ceremonies')
                elif index == 5:
                    self._dump(asset, 'competitive_tiers')
                elif index == 6:
                    self._dump(asset, 'content_tiers')
                elif index == 7:
                    self._dump(asset, 'contracts')
                elif index == 8:
                    self._dump(asset, 'currencies')
                elif index == 9:
                    self._dump(asset, 'events')
                elif index == 10:
                    self._dump(asset, 'game_modes')
                elif index == 11:
                    self._dump(asset, 'game_modes_equippables')
                elif index == 12:
                    self._dump(asset, 'gear')
                elif index == 13:
                    self._dump(asset, 'level_borders')
                elif index == 14:
                    self._dump(asset, 'maps')
                elif index == 15:
                    self._dump(asset, 'missions')
                elif index == 16:
                    self._dump(asset, 'player_cards')
                elif index == 17:
                    self._dump(asset, 'player_titles')
                elif index == 18:
                    self._dump(asset, 'seasons')
                elif index == 19:
                    self._dump(asset, 'seasons_competitive')
                elif index == 20:
                    self._dump(asset, 'sprays')
                elif index == 21:
                    self._dump(asset, 'themes')
                elif index == 22:
                    self._dump(asset, 'weapons')
                elif index == 23:
                    self._dump(asset, '_bundle_items')
                else:
                    print(f"Unknown asset type: {index}")

        if reload_asset:
            self.reload_assets(with_price=with_price)

    def reload_assets(self, with_price: bool = False):
        """
        Reload assets from disk.
        """
        _log.info("Reloading assets")

        self.ASSET_CACHE.clear()

        to_remove_dir = False
        for maybe_dir in sorted(
            os.listdir(self._cache_dir),
            key=lambda x: os.path.getmtime(os.path.join(self._cache_dir, x)),
            reverse=True,
        ):
            maybe_asset_dir = os.path.join(self._cache_dir, maybe_dir)
            if os.path.isdir(maybe_asset_dir) and str(maybe_dir).startswith('0'):
                if not to_remove_dir:
                    for filename in sorted(os.listdir(maybe_asset_dir), reverse=True):
                        if isinstance(filename, str) and filename.endswith('.json'):
                            file_path = os.path.join(str(maybe_asset_dir), filename)
                            with open(file_path, encoding='utf-8') as f:
                                to_dict = json.load(f)
                                if not filename.startswith('_offers'):
                                    self.__customize_asset_cache_format(filename, to_dict)
                                elif filename.startswith('_offers') and with_price:
                                    self.OFFER_CACHE.clear()
                                    self.OFFER_CACHE.update(to_dict)
                    to_remove_dir = True
                else:
                    shutil.rmtree(maybe_asset_dir)
                    _log.info(f'Removed asset directory {maybe_asset_dir}')

        _log.info("Assets reloaded")
        if with_price:
            _log.info("Offers reloaded")

    def _get_asset_dir(self) -> str:
        """Get the asset directory."""
        return os.path.join(Assets._cache_dir, self._client.version.version)

    @staticmethod
    def _get_asset_special_dir() -> str:
        """Get the asset special directory."""
        return os.path.join(Assets._cache_dir, 'special')

    def __mkdir_cache_dir(self) -> bool:
        """Make the assets' directory."""
        if not os.path.exists(self._cache_dir):
            try:
                os.mkdir(self._cache_dir)
            except OSError:
                return False
            else:
                # self.__mkdir_cache_gitignore()
                return True

    def __mkdir_assets_dir(self) -> bool:
        """Make the assets' directory."""
        assets_dir = self._get_asset_dir()
        if not os.path.exists(os.path.join(assets_dir)):
            try:
                os.mkdir(os.path.join(assets_dir))
            except OSError:
                _log.error(f'Failed to create asset directory')
                return False
            else:
                _log.info(f'Created asset directory')
                return True

    def __mkdir_cache_gitignore(self) -> None:
        """Make a .gitignore file in the assets' directory."""

        gitignore_path = os.path.join(self._cache_dir, ".gitignore")
        msg = "# This directory is used to assets data from the Valorant API.\n*\n"
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(msg)

    def _dump(self, data: Mapping[str, Any], filename: str) -> None:
        """Dump data to a file."""
        asset_path = self._get_asset_dir()
        file_path = os.path.join(asset_path, f'{filename}.json')

        for tries in range(3):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                break
            except FileNotFoundError:
                self.__mkdir_assets_dir()
                if tries == 3:
                    _log.error(f'Failed to create asset directory')
                    return

    def __special_weapons(self) -> None:
        listdir = os.listdir(self._get_asset_special_dir())
        for file in listdir:
            if file.endswith('.json'):
                with open(os.path.join(self._get_asset_special_dir(), file), encoding='utf-8') as f:
                    to_dict = json.load(f)
                    print(to_dict)

    @staticmethod
    def __customize_asset_cache_format(filename: str, data: Mapping[str, Any]) -> None:
        """Customize the asset assets format."""

        # TODO: additional asset weapons

        new_dict = {}
        buddy_level_dict = {}
        spray_level_dict = {}
        skin_dict = {}
        skin_level_dict = {}
        skin_chroma_dict = {}

        try:

            for item in data['data']:
                uuid = item['uuid']

                if filename.startswith('buddies'):
                    for buddy_level in item['levels']:
                        buddy_level['base_uuid'] = uuid
                        buddy_level_dict[buddy_level['uuid']] = buddy_level
                    Assets.ASSET_CACHE['buddies_levels'] = buddy_level_dict

                elif filename.startswith('sprays'):
                    for spray_level in item['levels']:
                        spray_level['base_uuid'] = uuid
                        spray_level_dict[spray_level['uuid']] = spray_level
                    Assets.ASSET_CACHE['sprays_levels'] = spray_level_dict

                elif filename.startswith('weapons'):

                    for skin in item['skins']:
                        skin['base_weapon_uuid'] = uuid
                        skin_dict[skin['uuid']] = skin

                        for skin_chroma in skin['chromas']:
                            skin_chroma['base_weapon_uuid'] = uuid
                            skin_chroma['base_skin_uuid'] = skin['uuid']
                            skin_chroma_dict[skin_chroma['uuid']] = skin_chroma
                        Assets.ASSET_CACHE['weapon_skins_chromas'] = skin_chroma_dict

                        for skin_level in skin['levels']:
                            skin_level['base_weapon_uuid'] = uuid
                            skin_level['base_skin_uuid'] = skin['uuid']
                            skin_level_dict[skin_level['uuid']] = skin_level
                        Assets.ASSET_CACHE['weapon_skins_levels'] = skin_level_dict

                    Assets.ASSET_CACHE['weapon_skins'] = skin_dict

                elif filename.startswith('_bundle_items'):
                    bundle = Assets.ASSET_CACHE['bundles'][uuid]
                    bundle['price'] = item['price']
                    bundle_items = []

                    def bundle_item_payload(**kwargs) -> Dict[str, Any]:
                        if kwargs['base_price'] is None:
                            kwargs['base_price'] = -1
                        return dict(
                            Item=dict(
                                ItemTypeID=kwargs['item_type_id'], ItemID=kwargs['item_id'], Amount=kwargs['amount']
                            ),  # noqa: E501
                            BasePrice=kwargs['base_price'],
                            CurrencyID=str(CurrencyID.valorant_point),
                            DiscountPercent=0,
                            DiscountedPrice=0,
                            IsPromoItem=False,
                        )

                    for weapon in item['weapons']:
                        bundle_items.append(
                            bundle_item_payload(
                                item_type_id=str(ItemType.skin),
                                item_id=weapon['levels'][0]['uuid'],
                                amount=1,
                                base_price=weapon.get('price', 0),
                            )
                        )
                    for buddy in item['buddies']:
                        bundle_items.append(
                            bundle_item_payload(
                                item_type_id=str(ItemType.buddy),
                                item_id=buddy['levels'][0]['uuid'],
                                amount=2,
                                base_price=buddy.get('price', 0),
                            )
                        )
                    for player_card in item['cards']:
                        bundle_items.append(
                            bundle_item_payload(
                                item_type_id=str(ItemType.player_card),
                                item_id=player_card['uuid'],
                                amount=1,
                                base_price=player_card.get('price', 0),
                            )
                        )
                    for spray in item['sprays']:
                        bundle_items.append(
                            bundle_item_payload(
                                item_type_id=str(ItemType.spray),
                                item_id=spray['uuid'],
                                amount=1,
                                base_price=spray.get('price', 0),
                            )
                        )
                    bundle['Items'] = bundle_items

                new_dict[uuid] = item

            Assets.ASSET_CACHE[filename[:-5]] = new_dict

        except KeyError as e:
            print(e)
            _log.error(f'Failed to customize asset cache format for {filename}')
