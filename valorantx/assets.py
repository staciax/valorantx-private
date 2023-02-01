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

import json
import logging
import os
import shutil
from functools import cache as _cache, wraps
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Tuple, TypeVar

from .enums import CurrencyType, ItemType
from .errors import AuthRequired
from .utils import MISSING, is_uuid

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from .client import Client
    from .models.version import Version

    P = ParamSpec('P')

T = TypeVar('T')

# fmt: off
__all__: Tuple[str, ...] = (
    'Assets',
)
# fmt: on

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
        return False
    elif isinstance(value, dict) and isinstance(key, str):
        for value_value in value.values():
            if _find(value_value, key):
                return True
        return False
    elif isinstance(value, dict) and isinstance(key, dict):
        for key_value in key.values():
            if _find(value, key_value):
                return True
        return False
    elif isinstance(value, list) and isinstance(key, str):
        for list_value in value:
            if _find(list_value, key):
                return True
        return False
    else:
        return False


def _finder():
    def decorator(function: Callable[P, T]) -> Callable[..., Mapping[Any, Any]]:
        @wraps(function)
        def wrapper(self: Assets, *args: P.args, **kwargs: P.kwargs) -> T:
            if not args and not kwargs:
                return function(self, uuid=None)

            new_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(key, str):
                    key = key.lower()
                if isinstance(value, str):
                    value = value.lower()
                if value is None:
                    value = '...'
                new_kwargs[key] = value

            kwargs = new_kwargs
            finder_keys = [x for x in list(kwargs.keys())]
            # inspired by https://github.com/MinshuG/valorant-api/blob/b739850d2722247b56b9e4d12caa8b3c326ce141/valorant_api/base_list.py#L17  # noqa: E501

            doc = function.__doc__
            if doc is None:
                get_key = '...'
            else:
                get_key = doc.split(',')[0].strip()
            data = Assets.ASSET_CACHE.get(get_key, {})

            if not data:
                return function(self, *args, **kwargs)

            is_level_border = False
            if len(finder_keys) == 0:
                may_be_uuid = args[0]
                if isinstance(may_be_uuid, str):
                    may_be_uuid = may_be_uuid.lower()

                if not is_uuid(str(may_be_uuid)) and not may_be_uuid == '':
                    if isinstance(may_be_uuid, int):
                        if get_key == 'level_borders':
                            kwargs['startinglevel'] = str(may_be_uuid)
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

                                    if int(kwargs[k]) > 20:
                                        next_level += 1

                                    if int(kwargs[k]) < next_level:
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
    _cache_dir: str = os.path.join(os.getcwd(), '.valorantx_cache')

    ASSET_CACHE = {}
    OFFER_CACHE = {}

    def __init__(self, *, client: Client) -> None:
        self._client = client
        self.version: Version = MISSING
        self._is_with_price: bool = False
        self._ready: bool = False

    def is_ready(self) -> bool:
        return self._ready

    @staticmethod
    def clear_cache() -> None:
        Assets.ASSET_CACHE.clear()

    @staticmethod
    def clear_offer_cache() -> None:
        Assets.OFFER_CACHE.clear()

    @staticmethod
    def clear() -> None:
        Assets.clear_cache()
        Assets.clear_offer_cache()

    def get_asset(self, key: str, tries: int = 3) -> Optional[Mapping[str, Any]]:
        """Get an asset."""
        if key in self.ASSET_CACHE:
            return self.ASSET_CACHE[key]

        for _ in range(tries):
            try:
                if key in self.ASSET_CACHE:
                    return self.ASSET_CACHE[key]
                else:
                    if _ >= tries:
                        _log.warning(f'Asset {key!r} not found')
                    raise KeyError(f"Asset {key!r} not found")
            except KeyError:
                self.reload(with_price=self._is_with_price)
                if _ >= tries - 1:
                    raise KeyError(f"Asset {key!r} not found")

    @_finder()
    def get_agent(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """agents, Get an agent by UUID."""
        data = self.get_asset('agents') or {}
        return data.get(uuid)

    @_finder()
    def get_buddy(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """buddies, Get a buddy by UUID."""
        data = self.get_asset('buddies') or {}
        return data.get(uuid)

    @_finder()
    def get_buddy_level(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """buddies_levels, Get a buddy level by UUID."""
        data = self.get_asset('buddies_levels') or {}
        return data.get(uuid)

    @_finder()
    def get_bundle(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """bundles, Get a bundle by UUID."""
        data = self.get_asset('bundles') or {}
        return data.get(uuid)

    @_finder()
    def get_ceremony(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """ceremonies, Get a ceremony by UUID."""
        data = self.get_asset('ceremonies') or {}
        return data.get(uuid)

    @_finder()
    def get_competitive_tier(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """competitive_tiers, Get a competitive tier by UUID."""
        data = self.get_asset('competitive_tiers') or {}
        return data.get(uuid)

    @_finder()
    def get_content_tier(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """content_tiers, Get a content tier by UUID."""
        data = self.get_asset('content_tiers') or {}
        return data.get(uuid)

    @_finder()
    def get_contract(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """contracts, Get a contract by UUID."""
        data = self.get_asset('contracts') or {}
        return data.get(uuid)

    @_finder()
    def get_currency(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """currencies, Get a currency by UUID."""
        data = self.get_asset('currencies') or {}
        return data.get(uuid)

    @_finder()
    def get_event(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """events, Get an event by UUID."""
        data = self.get_asset('events') or {}
        return data.get(uuid)

    @_finder()
    def get_game_mode(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """game_modes, Get a game mode by UUID."""
        data = self.get_asset('game_modes') or {}
        return data.get(uuid)

    @_finder()
    def get_game_mode_equippable(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """game_modes_equippables, Get a game mode equippable by UUID."""
        data = self.get_asset('game_modes_equippables') or {}
        return data.get(uuid)

    @_finder()
    def get_gear(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """gear, Get a gear by UUID."""
        data = self.get_asset('gear') or {}
        return data.get(uuid)

    @_finder()
    def get_level_border(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """level_borders, Get a level border by UUID."""
        data = self.get_asset('level_borders') or {}
        return data.get(uuid)

    @_finder()
    def get_map(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """maps, Get a map by UUID."""
        data = self.get_asset('maps') or {}
        return data.get(uuid)

    @_finder()
    def get_mission(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """missions, Get a mission by UUID."""
        data = self.get_asset('missions') or {}
        return data.get(uuid)

    @_finder()
    def get_player_card(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """player_cards, Get a player card by UUID."""
        data = self.get_asset('player_cards') or {}
        return data.get(uuid)

    @_finder()
    def get_player_title(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """player_titles, Get a player title by UUID."""
        data = self.get_asset('player_titles') or {}
        return data.get(uuid)

    @_finder()
    def get_season(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """seasons, Get a season by UUID."""
        data = self.get_asset('seasons') or {}
        return data.get(uuid)

    @_finder()
    def get_season_competitive(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """seasons_competitive, Get a season competitive by UUID."""
        data = self.get_asset('seasons_competitive') or {}
        return data.get(uuid)

    @_finder()
    def get_spray(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """sprays, Get a spray by UUID."""
        data = self.get_asset('sprays') or {}
        return data.get(uuid)

    @_finder()
    def get_spray_level(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """sprays_levels, Get a spray level by UUID."""
        data = self.get_asset('sprays_levels') or {}
        return data.get(uuid)

    @_finder()
    def get_theme(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """themes, Get a theme by UUID."""
        data = self.get_asset('themes') or {}
        return data.get(uuid)

    @_finder()
    def get_weapon(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """weapons, Get a weapon by UUID."""
        data = self.get_asset('weapons') or {}
        return data.get(uuid)

    @_finder()
    def get_skin(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """weapon_skins, Get a weapon skin by UUID."""
        data = self.get_asset('weapon_skins') or {}
        return data.get(uuid)

    @_finder()
    def get_skin_level(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """weapon_skins_levels, Get a weapon skin level by UUID."""
        data = self.get_asset('weapon_skins_levels') or {}
        return data.get(uuid)

    @_finder()
    def get_skin_chroma(self, uuid: str) -> Optional[Mapping[str, Any]]:
        """weapon_skins_chromas, Get a weapon skin chroma by UUID."""
        data = self.get_asset('weapon_skins_chromas') or {}
        return data.get(uuid)

    def get_item_price(self, uuid: str) -> int:
        return self.OFFER_CACHE.get(uuid, 0)

    async def fetch_assets(
        self,
        *,
        force: bool = False,
        with_price: bool = False,
        reload: bool = False,
        version: Optional[Version] = None,
    ) -> None:
        """Fetch all assets."""

        self._is_with_price = with_price

        get_version = version or await self._client.fetch_version()

        if get_version != self._client.version:
            self._client.version = get_version
            self.version = get_version

        self.__mkdir_dir()
        self.__mkdir_assets_dir()
        asset_path = self.__get_dir()

        # verify files exist
        list_dir = os.listdir(asset_path)
        if len([filename for filename in list_dir if filename.endswith('.json') and not filename.startswith('_')]) < 23:
            force = True
            if len(list_dir) > 0:
                _log.warning('some assets are missing, forcing update')

        # fetch offer/price of items

        if with_price:
            if not self._client.is_authorized():
                raise AuthRequired("You need to be authorized to fetch prices")
            if 'offers.json' not in list_dir:
                data = await self._client.fetch_offers()
                new_dict = {}
                for offer in data.offers:
                    new_dict[offer.id] = offer.cost
                self.__dump(new_dict, '_offers')
        else:
            if self._client.is_authorized():
                if not self.OFFER_CACHE:
                    _log.info('You can fetch items prices by calling `client.fetch_offers(with_price=True)`')
            else:
                _log.info('Skipping fetching items prices')

        if not asset_path.endswith(get_version.version) or len(os.listdir(self.__get_dir())) == 0 or force:
            _log.info(f"Fetching assets for version {get_version.version!r}")

            self.__dump(await self._client.http.asset_get_agents(), 'agents')
            self.__dump(await self._client.http.asset_get_buddies(), 'buddies')
            self.__dump(await self._client.http.asset_get_bundles(), 'bundles')
            self.__dump(await self._client.http.asset_get_ceremonies(), 'ceremonies')
            self.__dump(await self._client.http.asset_get_competitive_tiers(), 'competitive_tiers')
            self.__dump(await self._client.http.asset_get_content_tiers(), 'content_tiers')
            self.__dump(await self._client.http.asset_get_contracts(), 'contracts')
            self.__dump(await self._client.http.asset_get_currencies(), 'currencies')
            self.__dump(await self._client.http.asset_get_events(), 'events')
            self.__dump(await self._client.http.asset_get_game_modes(), 'game_modes')
            self.__dump(await self._client.http.asset_get_game_modes_equippables(), 'game_modes_equippables')
            self.__dump(await self._client.http.asset_get_gear(), 'gear')
            self.__dump(await self._client.http.asset_get_level_borders(), 'level_borders')
            self.__dump(await self._client.http.asset_get_maps(), 'maps')
            self.__dump(await self._client.http.asset_get_missions(), 'missions')
            self.__dump(await self._client.http.asset_get_player_cards(), 'player_cards')
            self.__dump(await self._client.http.asset_get_player_titles(), 'player_titles')
            self.__dump(await self._client.http.asset_get_seasons(), 'seasons')
            self.__dump(await self._client.http.asset_get_seasons_competitive(), 'seasons_competitive')
            self.__dump(await self._client.http.asset_get_sprays(), 'sprays')
            self.__dump(await self._client.http.asset_get_themes(), 'themes')
            self.__dump(await self._client.http.asset_get_weapons(), 'weapons')
            self.__dump(await self._client.http.asset_get_bundle_items(), 'bundles_2nd')

        if reload:
            self.reload(with_price=with_price)

        self._ready = True

    def reload(self, with_price: bool = False):
        """
        Reload assets from disk.
        """

        _log.info("Reloading assets")

        self._is_with_price = with_price

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
                    for filename in sorted(os.listdir(maybe_asset_dir)):
                        if isinstance(filename, str) and filename.endswith('.json'):
                            file_path = os.path.join(str(maybe_asset_dir), filename)
                            with open(file_path, encoding='utf-8') as f:
                                to_dict = json.load(f)
                                if not filename.startswith('_offers'):
                                    self.__to_cache(filename, to_dict)
                                elif filename.startswith('_offers') and with_price:
                                    self.OFFER_CACHE.clear()
                                    self.OFFER_CACHE.update(to_dict)
                    to_remove_dir = True
                else:
                    shutil.rmtree(maybe_asset_dir)
                    _log.info(f'Removed asset directory {maybe_asset_dir!r}')

        # self.__special_weapons()

        _log.info("Assets reloaded")
        if with_price:
            _log.info("Offers reloaded")

    @_cache
    def __get_dir(self) -> str:
        """:class:`str`: Get the asset directory."""
        return os.path.join(Assets._cache_dir, self._client.version.version)

    @staticmethod
    @_cache
    def __get_special_dir() -> str:
        """:class:`str`: The special weapon directory."""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        return os.path.join(path, 'specials')

    def __mkdir_dir(self) -> bool:
        """:return: True if the directory was created, False if it already exists."""
        if not os.path.exists(self._cache_dir):
            try:
                os.mkdir(self._cache_dir)
            except OSError:
                _log.error(f"Creation of the directory {self._cache_dir!r} failed")
                return False
            else:
                return True
        return False

    def __mkdir_assets_dir(self) -> bool:
        """Make the assets' directory."""
        assets_dir = self.__get_dir()
        if not os.path.exists(os.path.join(assets_dir)):
            try:
                os.mkdir(os.path.join(assets_dir))
            except OSError:
                _log.error(f'Failed to create asset directory')
                return False
            else:
                _log.info(f'Created asset directory')
                return True
        return False

    def __dump(self, data: Mapping[str, Any], filename: str) -> None:
        """Dump data to a file."""
        asset_path = self.__get_dir()
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
        """Special weapons."""

        special_dir = self.__get_special_dir()

        for filename in sorted(os.listdir(special_dir)):
            if isinstance(filename, str) and filename.endswith('.json'):
                file_path = os.path.join(str(special_dir), filename)
                with open(file_path, encoding='utf-8') as f:
                    to_dict = json.load(f)
                    if filename.startswith('weapons'):
                        self.ASSET_CACHE['weapons'].update(to_dict)

    @staticmethod
    def __to_cache(filename: str, data: Mapping[str, Any]) -> None:
        """Customize the asset assets format."""

        new_dict = {}
        buddy_level_payload = {}
        spray_level_payload = {}
        skin_payload = {}
        skin_level_payload = {}
        skin_chroma_payload = {}

        try:
            for item in data['data']:
                uuid = item['uuid']

                if filename.startswith('buddies'):
                    for index, buddy_level in enumerate(item['levels'], start=1):
                        buddy_level['BuddyID'] = uuid
                        buddy_level['levelNumber'] = index
                        buddy_level_payload[buddy_level['uuid']] = buddy_level
                    Assets.ASSET_CACHE['buddies_levels'] = buddy_level_payload

                elif filename.startswith('sprays'):
                    for spray_level in item['levels']:
                        spray_level['SprayID'] = uuid
                        spray_level_payload[spray_level['uuid']] = spray_level
                    Assets.ASSET_CACHE['sprays_levels'] = spray_level_payload

                elif filename.startswith('weapons'):
                    for skin in item['skins']:
                        skin['WeaponID'] = uuid
                        skin_payload[skin['uuid']] = skin

                        for skin_chroma in skin['chromas']:
                            skin_chroma['WeaponID'] = uuid
                            skin_chroma['SkinID'] = skin['uuid']
                            skin_chroma_payload[skin_chroma['uuid']] = skin_chroma
                        Assets.ASSET_CACHE['weapon_skins_chromas'] = skin_chroma_payload

                        for index, skin_level in enumerate(skin['levels'], start=1):
                            skin_level['WeaponID'] = uuid
                            skin_level['SkinID'] = skin['uuid']
                            skin_level['levelNumber'] = index
                            skin_level_payload[skin_level['uuid']] = skin_level
                        Assets.ASSET_CACHE['weapon_skins_levels'] = skin_level_payload

                    Assets.ASSET_CACHE['weapon_skins'] = skin_payload

                elif filename.startswith('bundles_2nd'):
                    bundle = Assets.ASSET_CACHE['bundles'][uuid]
                    bundle['price'] = item['price']
                    bundle_items = []

                    def bundle_item_payload(**kwargs) -> Mapping[str, Any]:
                        if kwargs['base_price'] is None:
                            kwargs['base_price'] = -1
                        return dict(
                            Item=dict(
                                ItemTypeID=kwargs['item_type_id'], ItemID=kwargs['item_id'], Amount=kwargs['amount']
                            ),  # noqa: E501
                            BasePrice=kwargs['base_price'],
                            CurrencyID=str(CurrencyType.valorant),
                            DiscountPercent=0,
                            DiscountedPrice=0,
                            IsPromoItem=False,
                        )

                    for weapon in item['weapons']:
                        bundle_items.append(
                            bundle_item_payload(
                                item_type_id=str(ItemType.skin_level),
                                item_id=weapon['levels'][0]['uuid'],
                                amount=1,
                                base_price=weapon.get('price', 0),
                            )
                        )
                    for buddy in item['buddies']:
                        bundle_items.append(
                            bundle_item_payload(
                                item_type_id=str(ItemType.buddy_level),
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
            _log.error(f'Failed to parse {filename!r} assets')
