from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Optional

from valorantx2.valorant_api.cache import CacheState as CacheStateValorantAPI

from .enums import CURRENCY_UUIDS, Locale
from .models.weapons import Skin, SkinChroma, SkinLevel, Weapon

if TYPE_CHECKING:
    from valorantx2.valorant_api.http import HTTPClient as HTTPClientValorantAPI
    from valorantx2.valorant_api.types import weapons

_log = logging.getLogger(__name__)


class CacheState(CacheStateValorantAPI):
    def __init__(self, *, locale: Locale, http: HTTPClientValorantAPI, to_file: bool = False) -> None:
        super().__init__(locale=locale, http=http, to_file=to_file)
        self._weapons: Dict[str, Weapon] = {}
        self._skins: Dict[str, Skin] = {}
        self._skin_chromas: Dict[str, SkinChroma] = {}
        self._skin_levels: Dict[str, SkinLevel] = {}

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

    def get_skin_level(self, uuid: Optional[str]) -> Optional[SkinLevel]:
        return self._skin_levels.get(uuid)  # type: ignore

    def insert_cost(self, uuid: str, cost: int) -> None:
        item = self.get_skin_level(uuid) or self.get_player_card(uuid) or self.get_buddy_level(uuid) or self.get_spray(uuid)
        if item is not None:
            item.cost = cost  # type: ignore
        else:
            if uuid in CURRENCY_UUIDS:
                return
            _log.warning(f'Could not find item with uuid {uuid!r} to insert cost {cost!r}')
