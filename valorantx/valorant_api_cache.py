# Copyright (c) 2023-present STACiA
# Licensed under the MIT

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from valorant.cache import CacheState as CacheStateValorantAPI

from .enums import ItemTypeID, Locale
from .models.buddies import Buddy
from .models.level_borders import LevelBorder
from .models.player_cards import PlayerCard
from .models.player_titles import PlayerTitle
from .models.sprays import Spray
from .models.weapons import Weapon

if TYPE_CHECKING:
    from valorant.types import buddies, level_borders, player_cards, player_titles, sprays, weapons

    from .models.buddies import BuddyLevel
    from .models.sprays import SprayLevel
    from .models.weapons import Skin, SkinChroma, SkinLevel
    from .valorant_api_client import HTTPClient

_log = logging.getLogger(__name__)

# fmt: off
__all__ = (
    'CacheState',
)
# fmt: on


class CacheState(CacheStateValorantAPI):
    http: HTTPClient

    if TYPE_CHECKING:
        _buddies: Dict[str, Buddy]
        _buddy_levels: Dict[str, BuddyLevel]
        _skins: Dict[str, Skin]
        _skin_chromas: Dict[str, SkinChroma]
        _skin_levels: Dict[str, SkinLevel]
        _sprays: Dict[str, Spray]
        _spray_levels: Dict[str, SprayLevel]
        _player_cards: Dict[str, PlayerCard]
        _weapons: Dict[str, Weapon]
        _player_titles: Dict[str, PlayerTitle]
        _level_borders: Dict[str, LevelBorder]

    def __init__(self, *, locale: Locale, http: HTTPClient, to_file: bool = False) -> None:
        super().__init__(locale=locale, http=http, to_file=to_file)

    async def init(self) -> None:
        await super().init()
        # valorant valtracker
        data = await self.http.get_bundles_valtracker()
        self._add_bundles_valtracker(data)

    def _add_bundles_valtracker(self, data: Any) -> None:
        bundle_data = data['data']
        for bundle in bundle_data:
            bd = self.get_bundle(bundle['uuid'])
            if bd is not None:
                for buddy in bundle['buddies']:
                    b = self.get_buddy(buddy['uuid'])
                    if b is not None:
                        bd._add_item(b)
                    else:
                        _log.warning('bundles valtracker missing buddy %s', buddy['uuid'])

                for card in bundle['cards']:
                    c = self.get_player_card(card['uuid'])
                    if c is not None:
                        bd._add_item(c)
                    else:
                        _log.warning('bundles valtracker missing card %s', card['uuid'])

                for spray in bundle['sprays']:
                    sp = self.get_spray(spray['uuid'])
                    if sp is not None:
                        bd._add_item(sp)
                    else:
                        _log.warning('bundles valtracker missing spray %s', spray['uuid'])

                for weapon in bundle['weapons']:
                    sk = self.get_skin(weapon['uuid'])
                    if sk is not None:
                        bd._add_item(sk)
                        # if sk.display_name.default.lower() != weapon['name'].lower():
                        #     _log.warning(f"{sk.display_name.default!r} ({sk.uuid}) != {weapon['name']!r} ({weapon['uuid']}) in bundle {bd.uuid!r}\n")
                    else:
                        _log.warning('bundles valtracker missing skin %s', weapon['uuid'])

    # buddies

    def store_buddy(self, data: buddies.Buddy) -> Buddy:
        buddy_id = data['uuid']
        self._buddies[buddy_id] = buddy = Buddy(state=self, data=data)
        for level in buddy.levels:
            self._buddy_levels[level.uuid] = level
        return buddy

    # player cards

    def store_player_card(self, data: player_cards.PlayerCard) -> PlayerCard:
        player_card_id = data['uuid']
        self._player_cards[player_card_id] = player_card = PlayerCard(state=self, data=data)
        return player_card

    # player titles

    def store_player_title(self, data: player_titles.PlayerTitle) -> PlayerTitle:
        player_title_id = data['uuid']
        self._player_titles[player_title_id] = player_title = PlayerTitle(state=self, data=data)
        return player_title

    # sprays

    def store_spray(self, data: sprays.Spray) -> Spray:
        spray_id = data['uuid']
        self._sprays[spray_id] = spray = Spray(state=self, data=data)
        for level in spray.levels:
            self._spray_levels[level.uuid] = level
        return spray

    # weapons

    def store_weapon(self, data: weapons.Weapon) -> Weapon:
        weapon_id = data['uuid']
        self._weapons[weapon_id] = weapon = Weapon(state=self, data=data)
        for skin in weapon.skins:
            self._skins[skin.uuid] = skin
            for chroma in skin.chromas:
                self._skin_chromas[chroma.uuid] = chroma
            for level in skin.levels:
                self._skin_levels[level.uuid] = level
        return weapon

    # level borders

    def store_level_border(self, data: level_borders.LevelBorder) -> LevelBorder:
        level_border_id = data['uuid']
        self._level_borders[level_border_id] = level_border = LevelBorder(state=self, data=data)
        return level_border

    if TYPE_CHECKING:

        def get_skin(self, uuid: Optional[str], /) -> Optional[Skin]:
            ...

        def get_skin_level(self, uuid: Optional[str], /) -> Optional[SkinLevel]:
            ...

        def get_skin_chroma(self, uuid: Optional[str], /) -> Optional[SkinChroma]:
            ...

        def get_player_card(self, uuid: Optional[str], /) -> Optional[PlayerCard]:
            ...

        def get_player_title(self, uuid: Optional[str], /) -> Optional[PlayerTitle]:
            ...

        def get_buddy_level(self, uuid: Optional[str], /) -> Optional[BuddyLevel]:
            ...

        def get_spray(self, uuid: Optional[str], /) -> Optional[Spray]:
            ...

        def get_spray_level(self, uuid: Optional[str], /) -> Optional[SprayLevel]:
            ...

        def get_buddy(self, uuid: Optional[str], /) -> Optional[Buddy]:
            ...

        def get_weapon(self, uuid: Optional[str], /) -> Optional[Weapon]:
            ...

        def get_level_border(self, uuid: Optional[str], /) -> Optional[LevelBorder]:
            ...

    def insert_cost(self, uuid: str, type: ItemTypeID, cost: int) -> None:
        if type is ItemTypeID.skin_level:
            self._insert_skin_level_cost(uuid, cost)
        elif type is ItemTypeID.player_card:
            self._insert_player_card_cost(uuid, cost)
        elif type is ItemTypeID.buddy_level:
            self._insert_buddy_level_cost(uuid, cost)
        elif type is ItemTypeID.spray:
            self._insert_spray_cost(uuid, cost)
        elif type is ItemTypeID.player_title:
            self._insert_player_title_cost(uuid, cost)
        elif type is ItemTypeID.currency:
            return
        else:
            _log.warning(f'Could not find item with uuid {uuid!r} to insert cost {cost!r}')

    def _insert_skin_level_cost(self, uuid: str, cost: int) -> None:
        item = self.get_skin_level(uuid)
        if item is not None:
            item.cost = cost

    def _insert_player_card_cost(self, uuid: str, cost: int) -> None:
        item = self.get_player_card(uuid)
        if item is not None:
            item.cost = cost

    def _insert_buddy_level_cost(self, uuid: str, cost: int) -> None:
        item = self.get_buddy_level(uuid)
        if item is not None:
            item.cost = cost

    def _insert_spray_cost(self, uuid: str, cost: int) -> None:
        item = self.get_spray(uuid)
        if item is not None:
            item.cost = cost

    def _insert_player_title_cost(self, uuid: str, cost: int) -> None:
        item = self.get_player_title(uuid)
        if item is not None:
            item.cost = cost
