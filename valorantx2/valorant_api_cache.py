from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Dict

from .enums import Locale  # CURRENCY_UUIDS
from .valorant_api.cache import CacheState as CacheStateValorantAPI

# from .models.weapons import Weapon, Skin, SkinChroma, SkinLevel
# from .models.player_cards import PlayerCard
from .models.bundles import Bundle

if TYPE_CHECKING:
    # from .valorant_api.types import weapons
    from .valorant_api.http import HTTPClient as HTTPClientValorantAPI

_log = logging.getLogger(__name__)


class CacheState(CacheStateValorantAPI):
    def __init__(self, *, locale: Locale, http: HTTPClientValorantAPI, to_file: bool = False) -> None:
        super().__init__(locale=locale, http=http, to_file=to_file)
        # self._weapons: Dict[str, Weapon] = {}
        # self._skins: Dict[str, Skin] = {}
        # self._skin_chromas: Dict[str, SkinChroma] = {}
        # self._skin_levels: Dict[str, SkinLevel] = {}

    def get_bundle(self, uuid: Optional[str]) -> Optional[Bundle]:
        return self._bundles.get(uuid)  # type: ignore

    def insert_cost(self, uuid: str, cost: int) -> None:
        ...
        # item = self.get_skin_level(uuid) or self.get_player_card(uuid) or self.get_buddy_level(uuid) or self.get_spray(uuid)
        # if item is not None:
        #     item.cost = cost
        # else:
        #     if uuid in CURRENCY_UUIDS:
        #         return
        #     _log.warning(f'Could not find item with uuid {uuid!r} to insert cost {cost!r}')
