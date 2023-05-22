# Copyright (c) 2023-present STACiA
# Licensed under the MIT license. Refer to the LICENSE file in the project root for more information.
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from aiohttp import ClientSession

from valorantx.valorant_api.client import Client as ClientValorantAPI
from valorantx.valorant_api.http import HTTPClient

from .enums import ItemType, Locale
from .models.store import Offers
from .valorant_api_cache import CacheState

if TYPE_CHECKING:
    from .models.buddies import Buddy, BuddyLevel
    from .models.level_borders import LevelBorder
    from .models.player_cards import PlayerCard
    from .models.player_titles import PlayerTitle
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
        player_titles: List[PlayerTitle]
        player_cards: List[PlayerCard]
        weapons: List[Weapon]

    def __init__(self, session: ClientSession, locale: Locale) -> None:
        super().__init__(session, locale)
        self.http: HTTPClient = HTTPClient(session)
        self.cache: CacheState = CacheState(locale=locale, http=self.http)

    def insert_cost(self, offers: Offers) -> None:
        for offer in offers.offers:
            for reward in offer.rewards:
                if not reward.type is ItemType.currency:
                    self.cache.insert_cost(reward.id, reward.type, offer.cost)

    # buddies

    if TYPE_CHECKING:

        def get_buddy(self, uuid: str) -> Optional[Buddy]:
            ...

        def get_buddy_level(self, uuid: str) -> Optional[BuddyLevel]:
            ...

        # weapons

        def get_weapon(self, uuid: str) -> Optional[Weapon]:
            ...

        def get_skin(self, uuid: str) -> Optional[Skin]:
            ...

        def get_skin_level(self, uuid: str) -> Optional[SkinLevel]:
            ...

        def get_skin_chroma(self, uuid: str) -> Optional[SkinChroma]:
            ...

        # sprays

        def get_spray(self, uuid: str) -> Optional[Spray]:
            ...

        def get_spray_level(self, uuid: str) -> Optional[SprayLevel]:
            ...

        # player cards

        def get_player_card(self, uuid: str) -> Optional[PlayerCard]:
            ...

        # player titles

        def get_player_title(self, uuid: str) -> Optional[PlayerTitle]:
            ...

        # level borders

        def get_level_border(self, uuid: str) -> Optional[LevelBorder]:
            ...
