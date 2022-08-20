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

import os
import json
import logging
import asyncio
import shutil

from pathlib import Path
from functools import wraps

from .models import (
    Agent,
    Buddy,
    BuddyLevel,
    Bundle,
    Contract,
    ContentTier,
    Weapon,
    Skin,
    SkinChroma,
    SkinLevel,
    PlayerCard,
    PlayerTitle,
    Spray,
    SprayLevel,
    Mission,
)

from .enums import Locale, ItemType
from .utils import is_uuid

from typing import Any, Iterator, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client

# fmt: off
__all__ = (
    'Assets',
)
# fmt: on

# TODO: assert function in get


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

def maybe_display_name(key: str = 'displayName'):

    def decorator(function):

        @wraps(function)
        def wrapper(uuid: str, *args) -> Any:

            if not isinstance(uuid, str):
                try:
                    may_be_uuid = args[0]
                except IndexError:
                    return function(uuid, *args)
            else:
                may_be_uuid = uuid

            if not is_uuid(str(may_be_uuid)):

                get_key = function.__doc__.split(',')[0].strip()
                data = Assets.ASSET_CACHE[get_key]

                for value in data.values():
                    display_names = value.get(key)
                    if display_names is not None:
                        for display_name in display_names.values():
                            if (
                                display_name.lower().startswith(may_be_uuid.lower())
                                or may_be_uuid.lower() == display_name.lower()
                            ):
                                args = (value['uuid'],)
                                return function(uuid, *args)

                raise ValueError('Invalid UUID')

            return function(uuid, *args)

        return wrapper

    return decorator


class Assets:

    _cache_dir: Path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "assets"
    )

    ASSET_CACHE = {}

    def __init__(self, *, client: Client, locale: Union[Locale, str] = Locale.american_english) -> None:
        self._client = client
        self.locale = locale

        # load assets
        self.reload_assets()

    @maybe_display_name()
    def get_agent(self, uuid: str) -> Optional[Agent]:
        """agents, Get an agent by UUID."""
        agents = self.ASSET_CACHE["agents"]
        data = agents.get(uuid)
        return Agent(client=self._client, data=data) if data is not None else None

    @maybe_display_name()
    def get_buddy(self, uuid: str) -> Optional[Union[Buddy, BuddyLevel]]:
        """buddies, Get a buddy by UUID."""
        buddies = self.ASSET_CACHE["buddies"]
        data = buddies.get(uuid)
        return Buddy(client=self._client, data=data) if data is not None else self.get_buddy_level(uuid)

    @maybe_display_name()
    def get_buddy_level(self, uuid: str) -> Optional[BuddyLevel]:
        """buddies_levels, Get a buddy level by UUID."""
        buddy_levels = self.ASSET_CACHE["buddies_levels"]
        data = buddy_levels.get(uuid)
        return BuddyLevel(client=self._client, data=data) if data is not None else None

    @maybe_display_name()
    def get_bundle(self, uuid: str) -> Optional[Bundle]:
        """bundles, Get a bundle by UUID."""
        bundles = self.ASSET_CACHE["bundles"]
        data = bundles.get(uuid)
        return Bundle(client=self._client, data=data) if data else None

    @validate_uuid
    def get_ceremonie(self, uuid: str) -> Any:
        """ceremonies, Get a ceremony by UUID."""
        data = self.ASSET_CACHE["ceremonies"]
        return data.get(uuid)

    @validate_uuid
    def get_competitive_tier(self, uuid: str) -> Any:
        """competitiveTiers, Get a competitive tier by UUID."""
        data = self.ASSET_CACHE["competitive_tiers"]
        return data.get(uuid)

    @validate_uuid
    def get_content_tier(self, uuid: str) -> Optional[ContentTier]:
        """content_tiers, Get a content tier by UUID."""
        content_tiers = self.ASSET_CACHE["content_tiers"]
        data = content_tiers.get(uuid)
        return ContentTier(client=self._client, data=data) if data else None

    @validate_uuid
    def get_contract(self, uuid: str) -> Optional[Contract]:
        """contracts, Get a contract by UUID."""
        contracts = self.ASSET_CACHE["contracts"]
        data = contracts.get(uuid)
        return Contract(client=self._client, data=data) if data else None

    @validate_uuid
    def get_currency(self, uuid: str) -> Any:
        """currencies, Get a currency by UUID."""
        data = self.ASSET_CACHE["currencies"]
        return data.get(uuid)

    @validate_uuid
    def get_game_mode(self, uuid: str) -> Any:
        """game_modes, Get a game mode by UUID."""
        data = self.ASSET_CACHE["game_modes"]
        return data.get(uuid)

    @validate_uuid
    def get_gear(self, uuid: str) -> Any:
        """gears, Get a gear by UUID."""
        data = self.ASSET_CACHE["gears"]
        return data.get(uuid)

    @validate_uuid
    def get_level_border(self, uuid: str) -> Any:
        """level_borders, Get a level border by UUID."""
        data = self.ASSET_CACHE["level_borders"]
        return data.get(uuid)

    @validate_uuid
    def get_map(self, uuid: str) -> Any:
        """maps, Get a map by UUID."""
        data = self.ASSET_CACHE["maps"]
        return data.get(uuid)

    @validate_uuid
    def get_mission(self, uuid: str) -> Optional[Mission]:
        """missions, Get a mission by UUID."""
        missions = self.ASSET_CACHE["missions"]
        data = missions.get(uuid)
        return Mission(client=self._client, data=data) if data else None

    @maybe_display_name()
    def get_player_card(self, uuid: str) -> Optional[PlayerCard]:
        """player_cards, Get a player card by UUID."""
        player_cards = self.ASSET_CACHE["player_cards"]
        data = player_cards.get(uuid)
        return PlayerCard(client=self._client, data=data) if data else None

    @maybe_display_name()
    def get_player_title(self, uuid: str) -> Optional[PlayerTitle]:
        """player_titles, Get a player title by UUID."""
        player_titles = self.ASSET_CACHE["player_titles"]
        data = player_titles.get(uuid)
        return PlayerTitle(client=self._client, data=data) if data else None

    @validate_uuid
    def get_season(self, uuid: str) -> Any:
        """seasons, Get a season by UUID."""
        data = self.ASSET_CACHE["seasons"]
        return data.get(uuid)

    @maybe_display_name()
    def get_spray(self, uuid: str) -> Optional[Union[Spray, SprayLevel]]:
        """sprays, Get a spray by UUID."""
        sprays = self.ASSET_CACHE["sprays"]
        data = sprays.get(uuid)
        return Spray(client=self._client, data=data) if data else self.get_spray_level(uuid)

    @maybe_display_name()
    def get_spray_level(self, uuid: str) -> Optional[SprayLevel]:
        """sprays_levels, Get a spray level by UUID."""
        spray_levels = self.ASSET_CACHE["sprays_levels"]
        data = spray_levels.get(uuid)
        return SprayLevel(client=self._client, data=data) if data is not None else None

    @validate_uuid
    def get_theme(self, uuid: str) -> Any:
        """themes, Get a theme by UUID."""
        data = self.ASSET_CACHE["themes"]
        return data.get(uuid)

    @maybe_display_name()
    def get_weapon(self, uuid: str) -> Optional[Weapon]:
        """weapons, Get a weapon by UUID."""
        weapons = self.ASSET_CACHE["weapons"]
        data = weapons.get(uuid)
        return Weapon(client=self._client, data=data) if data else None

    @maybe_display_name()
    def get_skin(self, uuid: str) -> Union[Skin, SkinChroma, SkinLevel]:
        """weapon_skins, Get a weapon skin by UUID."""
        skins = self.ASSET_CACHE["weapon_skins"]
        data = skins.get(uuid)
        return Skin(client=self._client, data=data) if data else None

    @maybe_display_name()
    def get_skin_level(self, uuid: str) -> Optional[Union[SkinLevel, SkinChroma]]:
        """weapon_skin_levels, Get a weapon skin level by UUID."""
        skin_levels = self.ASSET_CACHE["weapon_skin_levels"]
        data = skin_levels.get(uuid)
        return SkinLevel(client=self._client, data=data) if data else self.get_skin_chroma(uuid)

    @validate_uuid
    def get_skin_chroma(self, uuid: str) -> Optional[SkinChroma]:
        """weapon_skin_chromas, Get a weapon skin chroma by UUID."""
        skin_chromas = self.ASSET_CACHE["weapon_skin_chromas"]
        data = skin_chromas.get(uuid)
        return SkinChroma(client=self._client, data=data) if data else None

    def get_all_bundles(self) -> Iterator[Bundle]:
        for item in self.ASSET_CACHE["bundles"].values():
            yield Bundle(client=self._client, data=item)

    async def fetch_all_assets(self, *, force: bool = False) -> None:
        """Fetch all assets."""

        get_version = await self._client.http.get_valorant_version()

        if get_version != self._client.version:
            self._client.version = get_version

        # self.__mkdir_cache_dir()
        self.__mkdir_assets_dir()

        if (
            not self._get_asset_dir().endswith(self._client.version)
            or len(os.listdir(self._get_asset_dir())) == 0
            or force
        ):
            _log.info(f"Fetching assets for version {self._client.version!r}")

            async_tasks = [
                asyncio.ensure_future(self._client.http.asset_get_agent()),
                asyncio.ensure_future(self._client.http.asset_get_buddy()),
                asyncio.ensure_future(self._client.http.asset_get_bundle()),
                asyncio.ensure_future(self._client.http.asset_get_ceremonie()),
                asyncio.ensure_future(self._client.http.asset_get_competitive_tier()),
                asyncio.ensure_future(self._client.http.asset_get_content_tier()),
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
                    self.__dump_to(asset, 'content_tiers')
                elif index == 7:
                    self.__dump_to(asset, 'contracts')
                elif index == 8:
                    self.__dump_to(asset, 'currencies')
                elif index == 9:
                    self.__dump_to(asset, 'game_modes')
                elif index == 10:
                    self.__dump_to(asset, 'gears')
                elif index == 11:
                    self.__dump_to(asset, 'level_borders')
                elif index == 12:
                    self.__dump_to(asset, 'maps')
                elif index == 13:
                    self.__dump_to(asset, 'missions')
                elif index == 14:
                    self.__dump_to(asset, 'player_cards')
                elif index == 15:
                    self.__dump_to(asset, 'player_titles')
                elif index == 16:
                    self.__dump_to(asset, 'seasons')
                elif index == 17:
                    self.__dump_to(asset, 'sprays')
                elif index == 18:
                    self.__dump_to(asset, 'themes')
                elif index == 19:
                    self.__dump_to(asset, 'weapons')
                elif index == 20:
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
        return os.path.join(Assets._cache_dir, self._client.version)

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
        """Make the assets directory."""
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
        """Make a .gitignore file in the assets directory."""

        gitignore_path = os.path.join(self._cache_dir, ".gitignore")
        msg = "# This directory is used to assets data from the Valorant API.\n*\n"
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(msg)

    def __dump_to(self, data: Any, filename: str) -> None:
        """ Dump data to a file. """
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

        new_dict = {}
        buddy_level_dict = {}
        spray_level_dict = {}

        for item in data['data']:
            uuid = item['uuid']

            if filename.startswith('buddies'):
                for buddy_level in item['levels']:
                    buddy_level['default_uuid'] = uuid
                    buddy_level_dict[buddy_level['uuid']] = buddy_level
                Assets.ASSET_CACHE['buddies_levels'] = buddy_level_dict

            elif filename.startswith('sprays'):
                for spray_level in item['levels']:
                    spray_level['default_uuid'] = uuid
                    spray_level_dict[spray_level['uuid']] = spray_level
                Assets.ASSET_CACHE['sprays_levels'] = spray_level_dict

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
