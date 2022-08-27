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
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from .enums import ItemType, Locale
from .utils import is_uuid

if TYPE_CHECKING:
    from .client import Client

# fmt: off
__all__ = (
    'Assets',
)
# fmt: on

# TODO: assert function in get
# TODO: key error handling
# TODO: str, repr, eq, ne slots, for all classes

_log = logging.getLogger(__name__)


def check_uuid(value: str):
    assert value is not None
    if not is_uuid(str(value)):
        raise ValueError('Invalid UUID')


def validate_uuid(func):
    @wraps(func)
    def decorator(uuid, *args) -> Any:

        if isinstance(uuid, str):
            check_uuid(uuid)
            return func(uuid, *args)
        else:
            for arg in args:
                check_uuid(arg)
            return func(uuid, *args)

    return decorator


def maybe_uuid():  # TODO: rework this
    def decorator(function):
        @wraps(function)
        def wrapper(uuid: str, *args, **kwargs) -> Any:

            # TODO: kwargs option on or off and set key to find

            if not isinstance(uuid, str):
                try:
                    may_be_uuid = args[0]
                except IndexError:
                    return function(uuid, *args)
            else:
                may_be_uuid = uuid

            if not is_uuid(str(may_be_uuid)) and not may_be_uuid == '':

                get_key = function.__doc__.split(',')[0].strip()
                data = Assets.ASSET_CACHE.get(get_key, {})

                for value in data.values():
                    display_names = value.get('displayName')
                    if display_names is not None:
                        try:
                            for display_name in display_names.values():

                                if (
                                    display_name.lower().startswith(may_be_uuid.lower())
                                    or may_be_uuid.lower() == display_name.lower()
                                ):
                                    args = (value['uuid'],)
                                    return function(uuid, *args)

                        except AttributeError:
                            pass

                raise ValueError('Invalid UUID')

            return function(uuid, *args)

        return wrapper

    return decorator


class Assets:
    _cache_dir: Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    ASSET_CACHE = {}

    def __init__(self, *, client: Client, locale: Union[Locale, str] = Locale.american_english) -> None:
        self._client = client
        self.locale = locale

        # load assets
        self.reload_assets()

    def get_asset(self, key: str, tries: int = 1) -> Optional[Dict[str, Any]]:
        """Get an asset."""
        if key in self.ASSET_CACHE:
            return self.ASSET_CACHE[key]

        for _ in range(tries):
            self.reload_assets()
            if key in self.ASSET_CACHE:
                return self.ASSET_CACHE[key]
            else:
                raise KeyError(f"Asset {key!r} not found")

    @maybe_uuid()
    def get_agent(self, uuid: str) -> Optional[Dict[str, Any]]:
        """agents, Get an agent by UUID."""
        data = self.get_asset('agents')
        return data.get(uuid)

    @maybe_uuid()
    def get_buddy(self, uuid: str) -> Optional[Dict[str, Any]]:
        """buddies, Get a buddy by UUID."""
        data = self.get_asset('buddies')
        return data.get(uuid)

    @maybe_uuid()
    def get_buddy_level(self, uuid: str) -> Optional[Dict[str, Any]]:
        """buddies_levels, Get a buddy level by UUID."""
        data = self.get_asset('buddies_levels')
        return data.get(uuid)

    @maybe_uuid()
    def get_bundle(self, uuid: str) -> Optional[Dict[str, Any]]:
        """bundles, Get a bundle by UUID."""
        data = self.get_asset('bundles')
        return data.get(uuid)

    @maybe_uuid()
    def get_ceremony(self, uuid: str) -> Optional[Dict[str, Any]]:
        """ceremonies, Get a ceremony by UUID."""
        data = self.get_asset('ceremonies')
        return data.get(uuid)

    @validate_uuid
    def get_competitive_tier(self, uuid: str) -> Optional[Dict[str, Any]]:
        """competitive_tiers, Get a competitive tier by UUID."""
        data = self.get_asset('competitive_tiers')
        return data.get(uuid)

    @maybe_uuid()
    def get_content_tier(self, uuid: str) -> Optional[Dict[str, Any]]:
        """content_tiers, Get a content tier by UUID."""
        data = self.get_asset('content_tiers')
        return data.get(uuid)

    @maybe_uuid()
    def get_contract(self, uuid: str) -> Optional[Dict[str, Any]]:
        """contracts, Get a contract by UUID."""
        data = self.get_asset('contracts')
        return data.get(uuid)

    @maybe_uuid()
    def get_currency(self, uuid: str) -> Optional[Dict[str, Any]]:
        """currencies, Get a currency by UUID."""
        data = self.get_asset('currencies')
        return data.get(uuid)

    @maybe_uuid()
    def get_event(self, uuid: str) -> Optional[Dict[str, Any]]:
        """events, Get an event by UUID."""
        data = self.get_asset('events')
        return data.get(uuid)

    @maybe_uuid()
    def get_game_mode(self, uuid: str) -> Optional[Dict[str, Any]]:
        """game_modes, Get a game mode by UUID."""
        data = self.get_asset('game_modes')
        return data.get(uuid)

    @maybe_uuid()
    def get_game_mode_equippable(self, uuid: str) -> Optional[Dict[str, Any]]:
        """game_modes_equippables, Get a game mode equippable by UUID."""
        data = self.get_asset('game_modes_equippables')
        return data.get(uuid)

    @maybe_uuid()
    def get_gear(self, uuid: str) -> Optional[Dict[str, Any]]:
        """gear, Get a gear by UUID."""
        data = self.get_asset('gear')
        return data.get(uuid)

    @validate_uuid  # TODO : get by startingLevel
    def get_level_border(self, uuid: str) -> Optional[Dict[str, Any]]:
        """level_borders, Get a level border by UUID."""
        data = self.get_asset('level_borders')
        return data.get(uuid)

    @maybe_uuid()
    def get_map(self, uuid: str) -> Optional[Dict[str, Any]]:
        """maps, Get a map by UUID."""
        data = self.get_asset('maps')
        return data.get(uuid)

    @validate_uuid
    def get_mission(self, uuid: str) -> Optional[Dict[str, Any]]:
        """missions, Get a mission by UUID."""
        data = self.get_asset('missions')
        return data.get(uuid)

    @maybe_uuid()
    def get_player_card(self, uuid: str) -> Optional[Dict[str, Any]]:
        """player_cards, Get a player card by UUID."""
        data = self.get_asset('player_cards')
        return data.get(uuid)

    @maybe_uuid()
    def get_player_title(self, uuid: str) -> Optional[Dict[str, Any]]:
        """player_titles, Get a player title by UUID."""
        data = self.get_asset('player_titles')
        return data.get(uuid)

    @maybe_uuid()
    def get_season(self, uuid: str) -> Optional[Dict[str, Any]]:
        """seasons, Get a season by UUID."""
        data = self.get_asset('seasons')
        return data.get(uuid)

    @maybe_uuid()
    def get_spray(self, uuid: str) -> Optional[Dict[str, Any]]:
        """sprays, Get a spray by UUID."""
        data = self.get_asset('sprays')
        return data.get(uuid)

    @maybe_uuid()
    def get_spray_level(self, uuid: str) -> Optional[Dict[str, Any]]:
        """sprays_levels, Get a spray level by UUID."""
        data = self.get_asset('sprays_levels')
        return data.get(uuid)

    @maybe_uuid()
    def get_theme(self, uuid: str) -> Optional[Dict[str, Any]]:
        """themes, Get a theme by UUID."""
        data = self.get_asset('themes')
        return data.get(uuid)

    @maybe_uuid()
    def get_weapon(self, uuid: str) -> Optional[Dict[str, Any]]:
        """weapons, Get a weapon by UUID."""
        data = self.get_asset('weapons')
        return data.get(uuid)

    @maybe_uuid()
    def get_skin(self, uuid: str) -> Optional[Dict[str, Any]]:
        """weapon_skins, Get a weapon skin by UUID."""
        data = self.get_asset('weapon_skins')
        return data.get(uuid)

    @maybe_uuid()
    def get_skin_level(self, uuid: str) -> Optional[Dict[str, Any]]:
        """weapon_skins_levels, Get a weapon skin level by UUID."""
        data = self.get_asset('weapon_skins_levels')
        return data.get(uuid)

    @maybe_uuid()
    def get_skin_chroma(self, uuid: str) -> Optional[Dict[str, Any]]:
        """weapon_skins_chromas, Get a weapon skin chroma by UUID."""
        data = self.get_asset('weapon_skins_chromas')
        return data.get(uuid)

    async def fetch_all_assets(self, *, force: bool = False) -> None:
        """Fetch all assets."""

        get_version = await self._client.get_valorant_version()

        if get_version != self._client.version:
            self._client.version = get_version

        # self.__mkdir_cache_dir()
        self.__mkdir_assets_dir()

        if (
            not self._get_asset_dir().endswith(self._client.version.version)
            or len(os.listdir(self._get_asset_dir())) == 0
            or force
        ):
            _log.info(f"Fetching assets for version {self._client.version.version!r}")

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
                asyncio.ensure_future(self._client.http.asset_get_sprays()),
                asyncio.ensure_future(self._client.http.asset_get_themes()),
                asyncio.ensure_future(self._client.http.asset_get_weapons()),
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
                    self.__dump_to(asset, 'content_tiers')
                elif index == 7:
                    self.__dump_to(asset, 'contracts')
                elif index == 8:
                    self.__dump_to(asset, 'currencies')
                elif index == 9:
                    self.__dump_to(asset, 'events')
                elif index == 10:
                    self.__dump_to(asset, 'game_modes')
                elif index == 11:
                    self.__dump_to(asset, 'game_modes_equippables')
                elif index == 12:
                    self.__dump_to(asset, 'gear')
                elif index == 13:
                    self.__dump_to(asset, 'level_borders')
                elif index == 14:
                    self.__dump_to(asset, 'maps')
                elif index == 15:
                    self.__dump_to(asset, 'missions')
                elif index == 16:
                    self.__dump_to(asset, 'player_cards')
                elif index == 17:
                    self.__dump_to(asset, 'player_titles')
                elif index == 18:
                    self.__dump_to(asset, 'seasons')
                elif index == 19:
                    self.__dump_to(asset, 'sprays')
                elif index == 20:
                    self.__dump_to(asset, 'themes')
                elif index == 21:
                    self.__dump_to(asset, 'weapons')
                elif index == 22:
                    self.__dump_to(asset, '_bundle_items')
                else:
                    print(f"Unknown asset type: {index}")

        self.reload_assets()

    def reload_assets(self) -> None:
        """Reload assets."""

        _log.info("Reloading assets")

        self.ASSET_CACHE.clear()
        self.__load_assets()

        _log.info("Assets reloaded")

    def _get_asset_dir(self) -> str:
        """Get the asset directory."""
        return os.path.join(Assets._cache_dir, self._client.version.version)

    def __load_assets(self) -> None:
        """Load assets."""

        # self.__mkdir_cache_dir()

        to_remove_dir = False

        for maybe_dir in sorted(
            os.listdir(self._cache_dir),
            key=lambda x: os.path.getmtime(os.path.join(self._cache_dir, x)),
            reverse=True,
        ):
            maybe_asset_dir = os.path.join(self._cache_dir, maybe_dir)
            if os.path.isdir(maybe_asset_dir) and str(maybe_dir).startswith('0'):
                if not to_remove_dir:
                    for filename in os.listdir(maybe_asset_dir):
                        if isinstance(filename, str) and filename.endswith('.json'):
                            Assets.__to_cache(str(maybe_asset_dir), str(filename))
                    to_remove_dir = True
                else:
                    shutil.rmtree(maybe_asset_dir)
                    _log.info(f'Removed asset directory {maybe_asset_dir}')

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

    def __dump_to(self, data: Any, filename: str) -> None:
        """Dump data to a file."""
        file_path = os.path.join(self._get_asset_dir(), f'{filename}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def __to_cache(path: str, filename: str) -> None:
        """Add data to the assets."""
        file_path = os.path.join(path, filename)
        with open(file_path, encoding='utf-8') as f:
            to_dict = json.load(f)
            Assets.__customize_asset_cache_format(filename, to_dict)

    @staticmethod
    def __customize_asset_cache_format(filename: str, data: Any) -> None:
        """Customize the asset assets format."""

        # TODO: additional asset weapons

        new_dict = {}
        buddy_level_dict = {}
        spray_level_dict = {}
        skin_dict = {}
        skin_level_dict = {}
        skin_chroma_dict = {}

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
                default_payload = dict(amount=1, discount=0)
                for weapon in item['weapons']:
                    bundle_items.append(
                        dict(
                            uuid=weapon['levels'][0]['uuid'],
                            type=str(ItemType.skin),
                            price=weapon.get('price', 0),
                            **default_payload,
                        )
                    )
                for buddy in item['buddies']:
                    bundle_items.append(
                        dict(
                            uuid=buddy['uuid'],
                            type=str(ItemType.buddy),
                            price=buddy.get('price', 0),
                            **default_payload,
                        )
                    )
                for card in item['cards']:
                    bundle_items.append(
                        dict(
                            uuid=card['uuid'],
                            type=str(ItemType.player_card),
                            price=card.get('price', 0),
                            **default_payload,
                        )
                    )
                for spray in item['sprays']:
                    bundle_items.append(
                        dict(
                            uuid=spray['uuid'],
                            type=str(ItemType.spray),
                            price=spray.get('price', 0),
                            **default_payload,
                        )
                    )
                bundle['items'] = bundle_items

            new_dict[uuid] = item

        Assets.ASSET_CACHE[filename[:-5]] = new_dict
