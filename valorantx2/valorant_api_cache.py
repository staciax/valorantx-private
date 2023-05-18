# Copyright (c) 2023-present STACiA
# Licensed under the MIT

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Optional

from valorantx2.valorant_api.cache import CacheState as CacheStateValorantAPI

from .enums import ItemType, Locale
from .models.buddies import Buddy
from .models.player_cards import PlayerCard
from .models.player_titles import PlayerTitle
from .models.sprays import Spray
from .models.weapons import Weapon

if TYPE_CHECKING:
    from valorantx2.valorant_api.http import HTTPClient as HTTPClientValorantAPI
    from valorantx2.valorant_api.types import buddies, player_cards, player_titles, sprays, weapons

    from .models.buddies import BuddyLevel
    from .models.sprays import SprayLevel
    from .models.weapons import Skin, SkinChroma, SkinLevel

_log = logging.getLogger(__name__)

# fmt: off
__all__ = (
    'CacheState',
)
# fmt: on


class CacheState(CacheStateValorantAPI):
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

    def __init__(self, *, locale: Locale, http: HTTPClientValorantAPI, to_file: bool = False) -> None:
        super().__init__(locale=locale, http=http, to_file=to_file)

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

    if TYPE_CHECKING:

        def get_skin_level(self, uuid: Optional[str]) -> Optional[SkinLevel]:
            ...

        def get_player_card(self, uuid: Optional[str]) -> Optional[PlayerCard]:
            ...

        def get_buddy_level(self, uuid: Optional[str]) -> Optional[BuddyLevel]:
            ...

        def get_spray(self, uuid: Optional[str]) -> Optional[Spray]:
            ...

        def get_buddy(self, uuid: Optional[str]) -> Optional[Buddy]:
            ...

        def get_weapon(self, uuid: Optional[str]) -> Optional[Weapon]:
            ...

    def insert_cost(self, uuid: str, type: ItemType, cost: int) -> None:
        if type is ItemType.skin_level:
            self._insert_skin_level_cost(uuid, cost)
        elif type is ItemType.player_card:
            self._insert_player_card_cost(uuid, cost)
        elif type is ItemType.buddy_level:
            self._insert_buddy_level_cost(uuid, cost)
        elif type is ItemType.spray:
            self._insert_spray_cost(uuid, cost)
        elif type is ItemType.currency:
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
