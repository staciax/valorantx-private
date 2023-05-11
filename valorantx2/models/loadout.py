from __future__ import annotations

import logging

# TODO: loadoutbuilder
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from ..enums import LevelBorderID, SpraySlotID

if TYPE_CHECKING:
    from ..client import Client
    from ..types.loadout import (
        Gun as GunPayload,
        Identity as IdentityPayload,
        Loadout as LoadoutPayload,
        Spray as SprayPayload,
    )
    from .buddies import Buddy, BuddyLevel
    from .level_borders import LevelBorder
    from .player_cards import PlayerCard
    from .player_titles import PlayerTitle
    from .sprays import Spray, SprayLevel
    from .weapons import Skin, SkinChroma, SkinLevel, Weapon

_log = logging.getLogger(__name__)


__all__ = (
    'Loadout',
    'Identity',
    'GunLoadout',
    'SprayLoadout',
)


class Identity:
    def __init__(self, client: Client, data: IdentityPayload) -> None:
        self._client = client
        self._player_card_id: str = data['PlayerCardID']
        self._player_title_id: str = data['PlayerTitleID']
        self.account_level: int = data['AccountLevel']
        self._preferred_level_border_id: str = data['PreferredLevelBorderID']
        self.hide_account_level: bool = data['HideAccountLevel']
        self._player_card: Optional[PlayerCard] = None
        self._player_title: Optional[PlayerTitle] = None
        self._preferred_level_border: Optional[LevelBorder] = None

        # player card
        self.player_card = self._client.valorant_api.get_player_card(self._player_card_id)
        if self.player_card is None:
            _log.warning(f'player card {self._player_card_id!r} not found')

        # player title
        self.player_title = self._client.valorant_api.get_player_title(self._player_title_id)
        if self.player_title is None:
            _log.warning(f'player title {self._player_title_id!r} not found')

        # level border
        if self._preferred_level_border_id != LevelBorderID.empty.value:
            self.preferred_level_border = self._client.valorant_api.get_level_border(self._preferred_level_border_id)
            if self.preferred_level_border is None:
                _log.warning(f'level border {self._preferred_level_border_id!r} not found')

    @property
    def player_card(self) -> Optional[PlayerCard]:
        return self._player_card

    @player_card.setter
    def player_card(self, value: Optional[PlayerCard]) -> None:
        self._player_card = value

    @property
    def player_title(self) -> Optional[PlayerTitle]:
        return self._player_title

    @player_title.setter
    def player_title(self, value: Optional[PlayerTitle]) -> None:
        self._player_title = value

    @property
    def preferred_level_border(self) -> Optional[LevelBorder]:
        return self._preferred_level_border

    @preferred_level_border.setter
    def preferred_level_border(self, value: Optional[LevelBorder]) -> None:
        self._preferred_level_border = value


class GunLoadout:
    def __init__(self, client: Client, data: GunPayload) -> None:
        self._client: Client = client
        self.id: str = data['ID']
        self._skin_id: str = data['SkinID']
        self._skin_level_id: str = data['SkinLevelID']
        self._chroma_id: str = data['ChromaID']
        self._charm_instance_id: Optional[str] = data.get('CharmInstanceID')
        self._charm_id: Optional[str] = data.get('CharmID')
        self._charm_level_id: Optional[str] = data.get('CharmLevelID')
        self.attachments: List[Any] = data['Attachments']

    def get_weapon(self) -> Optional[Weapon]:
        return self._client.valorant_api.get_weapon(self.id)

    def get_skin(self) -> Optional[Skin]:
        return self._client.valorant_api.get_skin(self._skin_id)

    def get_skin_level(self) -> Optional[SkinLevel]:
        return self._client.valorant_api.get_skin_level(self._skin_level_id)

    def get_skin_chroma(self) -> Optional[SkinChroma]:
        return self._client.valorant_api.get_skin_chroma(self._chroma_id)

    def get_charm(self) -> Optional[Buddy]:
        if self._charm_id is None:
            return None
        return self._client.valorant_api.get_buddy(self._charm_id)

    def get_charm_level(self) -> Optional[BuddyLevel]:
        if self._charm_level_id is None:
            return None
        return self._client.valorant_api.get_buddy_level(self._charm_level_id)

    # aliases

    def get_buddy(self) -> Optional[Buddy]:
        return self.get_charm()

    def get_buddy_level(self) -> Optional[BuddyLevel]:
        return self.get_charm_level()


class SprayLoadout:
    def __init__(self, client: Client, data: SprayPayload) -> None:
        self._client: Client = client
        self.equip_slot_id: str = data['EquipSlotID']
        self._spray_id: str = data['SprayID']
        self._spray_level_id: Optional[str] = data['SprayLevelID']
        # cache spray and spray level
        self._spray: Optional[Spray] = self._client.valorant_api.get_spray(self._spray_id)
        self._spray_level: Optional[SprayLevel] = None
        if self._spray_level_id is not None:
            self._spray_level = self._client.valorant_api.get_spray_level(self._spray_level_id)

    @property
    def slot_number(self) -> int:
        if self.equip_slot_id == SpraySlotID.slot_1.value:
            return 0
        elif self.equip_slot_id == SpraySlotID.slot_2.value:
            return 1
        elif self.equip_slot_id == SpraySlotID.slot_3.value:
            return 2
        return -1

    def get_spray(self) -> Optional[Spray]:
        return self._spray

    def get_spray_level(self) -> Optional[SprayLevel]:
        return self._spray_level


class Loadout:
    def __init__(self, client: Client, data: LoadoutPayload) -> None:
        self._client: Client = client
        self.subject: str = data['Subject']
        self.version: int = data['Version']
        self._guns: Dict[str, GunLoadout] = {gun['ID']: GunLoadout(self._client, gun) for gun in data['Guns']}
        self._sprays: Dict[int, SprayLoadout] = {}
        self.identity: Identity = Identity(self._client, data['Identity'])
        self.incognito: bool = data['Incognito']
        for spray in data['Sprays']:
            spray_loadout = SprayLoadout(self._client, spray)
            self.sprays[spray_loadout.slot_number] = spray_loadout

    def __repr__(self) -> str:
        return f'<Loadout subject={self.subject!r} version={self.version}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Loadout) and (self.version == other.version or self.incognito == other.incognito)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.subject, self.version, self.incognito))

    @property
    def guns(self) -> List[GunLoadout]:
        return list(self._guns.values())

    def get_gun(self, gun_id: str) -> Optional[GunLoadout]:
        return self._guns.get(gun_id)

    @property
    def sprays(self) -> List[SprayLoadout]:
        return list(self._sprays.values())

    def get_spray(self, slot_number: Literal[0, 1, 2]) -> Optional[SprayLoadout]:
        return self._sprays.get(slot_number)

    async def _update_account_xp(self) -> None:
        ...

    #     account_xp = await self._client.fetch_account_xp()
    #     self._client.user.account_level = account_xp.level
    #     self.identity.account_level = account_xp.level

    async def _update_favorites(self):
        ...

    #     favorite = await self._client.fetch_favorites()
    #     for i_fav in favorite.items:
    #         if i_fav.type == ItemType.skin:
    #             for i_skin in self._skins:
    #                 if i_skin is not None:
    #                     skin_loadout = i_skin.get_skin() if i_skin.type != ItemType.skin else i_skin
    #                     if skin_loadout is not None:
    #                         if skin_loadout == i_fav:
    #                             i_skin.to_favorite()

    #         if i_fav.type == ItemType.buddy:
    #             for i_skin in self._skins:
    #                 if i_skin is not None:
    #                     skin_buddy = i_skin.get_buddy()
    #                     if skin_buddy is not None:
    #                         if skin_buddy == i_fav:
    #                             skin_buddy.to_favorite()

    #         if i_fav.type == ItemType.spray:
    #             for i_spray in self.get_sprays():
    #                 if i_spray is not None:
    #                     if i_spray == i_fav:
    #                         i_spray.to_favorite()

    #         if i_fav.type == ItemType.player_card:
    #             player_card = self.get_player_card()
    #             if player_card == i_fav:
    #                 if player_card is not None:
    #                     player_card.to_favorite()

    #         if i_fav.type == ItemType.level_border:
    #             level_border = self.get_level_border()
    #             if level_border is not None:
    #                 if level_border == i_fav:
    #                     level_border.to_favorite()


class LoadoutBuilder:
    ...  # TODO: implement
