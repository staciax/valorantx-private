from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import Locale
from .valorant_api.cache import CacheState as CacheStateValorantAPI

if TYPE_CHECKING:
    from .valorant_api.http import HTTPClient as HTTPClientValorantAPI

# from .models.store import Offer, Offers


class CacheState(CacheStateValorantAPI):
    def __init__(self, *, locale: Locale, http: HTTPClientValorantAPI, to_file: bool = False) -> None:
        super().__init__(locale=locale, http=http, to_file=to_file)

    def insert_cost(self, uuid: str, cost: int) -> None:
        ...
        # self.cost = cost
