# Copyright (c) 2023-present STACiA
# Licensed under the MIT license. Refer to the LICENSE file in the project root for more information.
from __future__ import annotations

from typing import TYPE_CHECKING, List

from aiohttp import ClientSession

from valorantx2.valorant_api.client import Client as ClientValorantAPI
from valorantx2.valorant_api.http import HTTPClient

from .enums import ItemType, Locale
from .models.store import Offers
from .valorant_api_cache import CacheState

if TYPE_CHECKING:
    from .models.buddies import Buddy, BuddyLevel
    from .models.player_cards import PlayerCard
    from .models.sprays import Spray, SprayLevel
    from .models.weapons import Skin, SkinChroma, SkinLevel, Weapon

# fmt: off
__all__ = (
    'Client',
)
# fmt: on


class Client(ClientValorantAPI):
    if TYPE_CHECKING:
        buddies: List[Buddy]
        buddy_levels: List[BuddyLevel]
        skins: List[Skin]
        skin_chromas: List[SkinChroma]
        skin_levels: List[SkinLevel]
        sprays: List[Spray]
        spray_levels: List[SprayLevel]
        player_cards: List[PlayerCard]
        weapons: List[Weapon]

    def __init__(self, session: ClientSession, locale: Locale) -> None:
        super().__init__(session, locale)
        self.http: HTTPClient = HTTPClient(session)
        self._cache: CacheState = CacheState(locale=locale, http=self.http)

    def insert_cost(self, offers: Offers) -> None:
        for offer in offers.offers:
            for reward in offer.rewards:
                if not reward.type is ItemType.currency:
                    self._cache.insert_cost(reward.id, reward.type, offer.cost)
