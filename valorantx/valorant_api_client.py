# Copyright (c) 2023-present STACiA
# Licensed under the MIT license. Refer to the LICENSE file in the project root for more information.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from aiohttp import ClientSession
from valorant.client import Client as ClientValorantAPI
from valorant.http import HTTPClient as HTTPClientValorantAPI
from valorant.models.maps import Map
from valorant.models.seasons import CompetitiveSeason

from .enums import ItemTypeID, Locale
from .http import Route
from .models.store import Offers
from .valorant_api_cache import CacheState

if TYPE_CHECKING:
    from valorant.http import Response

    from .models.buddies import Buddy, BuddyLevel
    from .models.competitive_tiers import Tier
    from .models.gamemodes import GameMode
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


class HTTPClient(HTTPClientValorantAPI):
    # valtracker endpoint

    def get_bundles_valtracker(self) -> Response[Any]:
        r = Route.from_url('GET', 'https://api.valtracker.gg/v1/bundles')
        return self.request(r)  # type: ignore


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
        super().__init__(locale)
        self.http: HTTPClient = HTTPClient(session)
        self.cache: CacheState = CacheState(locale=locale, http=self.http)

    def insert_cost(self, offers: Offers) -> None:
        for offer in offers.offers:
            for reward in offer.rewards:
                if not reward.type is ItemTypeID.currency:
                    self.cache.insert_cost(reward.id, reward.type, offer.cost)

    # buddies

    if TYPE_CHECKING:

        def get_buddy(self, uuid: str, /) -> Optional[Buddy]:
            ...

        def get_buddy_level(self, uuid: str, /) -> Optional[BuddyLevel]:
            ...

        # weapons

        def get_weapon(self, uuid: str, /) -> Optional[Weapon]:
            ...

        def get_skin(self, uuid: str, /) -> Optional[Skin]:
            ...

        def get_skin_level(self, uuid: str, /) -> Optional[SkinLevel]:
            ...

        def get_skin_chroma(self, uuid: str, /) -> Optional[SkinChroma]:
            ...

        # sprays

        def get_spray(self, uuid: str, /) -> Optional[Spray]:
            ...

        def get_spray_level(self, uuid: str, /) -> Optional[SprayLevel]:
            ...

        # player cards

        def get_player_card(self, uuid: str, /) -> Optional[PlayerCard]:
            ...

        # player titles

        def get_player_title(self, uuid: str, /) -> Optional[PlayerTitle]:
            ...

        # level borders

        def get_level_border(self, uuid: str, /) -> Optional[LevelBorder]:
            ...

    # custom

    def get_map_by_url(self, url: str, /) -> Optional[Map]:
        for map in self.cache.maps:
            if map.url == url:
                return map
        return None

    def get_game_mode_by_url(self, url: str, /) -> Optional[GameMode]:
        if url == '/Game/GameModes/Bomb/BombGameMode.BombGameMode_C':
            return self.get_game_mode('96bd3920-4f36-d026-2b28-c683eb0bcac5')
        elif url == '/Game/GameModes/Deathmatch/DeathmatchGameMode.DeathmatchGameMode_C':
            return self.get_game_mode('a8790ec5-4237-f2f0-e93b-08a8e89865b2')
        elif url == '/Game/GameModes/GunGame/GunGameTeamsGameMode.GunGameTeamsGameMode_C':
            return self.get_game_mode('a4ed6518-4741-6dcb-35bd-f884aecdc859')
        elif url == '/Game/GameModes/OneForAll/OneForAll_GameMode.OneForAll_GameMode_C':
            return self.get_game_mode('4744698a-4513-dc96-9c22-a9aa437e4a58')
        elif url == '/Game/GameModes/QuickBomb/QuickBombGameMode.QuickBombGameMode_C':
            return self.get_game_mode('e921d1e6-416b-c31f-1291-74930c330b7b')
        elif url == '/Game/GameModes/SnowballFight/SnowballFightGameMode.SnowballFightGameMode_C':
            return self.get_game_mode('57038d6d-49b1-3a74-c5ef-3395d9f23a97')
        elif url == '/Game/GameModes/ShootingRange/ShootingRangeGameMode.ShootingRangeGameMode_C':
            return self.get_game_mode('e2dc3878-4fe5-d132-28f8-3d8c259efcc6')
        elif url == '/Game/GameModes/NewPlayerExperience/NPEGameMode.NPEGameMode_C':
            return self.get_game_mode('d2b4e425-4cab-8d95-eb26-bb9b444551dc')
        elif (
            url
            == '/Game/GameModes/_Development/Swiftplay_EndOfRoundCredits/Swiftplay_EoRCredits_GameMode.Swiftplay_EoRCredits_GameMode_C'
        ):
            return self.get_game_mode('5d0f264b-4ebe-cc63-c147-809e1374484b')
        return None

    def get_competitive_season_by_season_id(self, season_id: str, /) -> Optional[CompetitiveSeason]:
        for ss_com in self.competitive_seasons:
            if ss_com.season is None:
                continue
            if ss_com.season.id == season_id:
                return ss_com
        return None

    def get_tier(self, season_id: str, tier: int) -> Optional[Tier]:
        competitive_season = self.get_competitive_season_by_season_id(season_id)
        if competitive_season is None:
            return None
        if competitive_season.competitive_tiers is None:
            return None
        for t in competitive_season.competitive_tiers.tiers:
            if t.tier == tier:
                return t
        return None
