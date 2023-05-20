from __future__ import annotations

import logging

# TODO: loadoutbuilder
from typing import TYPE_CHECKING, Dict, Iterator, List, Literal, Optional, Union

from valorantx.models.weapons import Weapon
from valorantx.valorant_api_cache import CacheState

from ..enums import LevelBorderID, SpraySlotID
from .weapons import Skin, SkinChroma, SkinLevel, Weapon

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.weapons import (
        Skin as ValorantAPISkinPayload,
        SkinChroma as ValorantAPISkinChromaPayload,
        SkinLevel as ValorantAPISkinLevelPayload,
        Weapon as ValorantAPIWeaponPayload,
    )

    from ..client import Client
    from ..types.loadout import (
        Gun as GunPayload,
        Identity as IdentityPayload,
        Loadout as LoadoutPayload,
        Spray as SprayPayload,
    )
    from ..valorant_api_cache import CacheState
    from .buddies import Buddy, BuddyLevel
    from .favorites import Favorites
    from .level_borders import LevelBorder
    from .player_cards import PlayerCard
    from .player_titles import PlayerTitle
    from .sprays import Spray, SprayLevel


_log = logging.getLogger(__name__)

__all__ = (
    'Loadout',
    'Identity',
    'SprayLoadout',
)


class SkinLoadout(Skin):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinPayload, parent: Weapon) -> None:
        super().__init__(state=state, data=data, parent=parent)


class SkinChromaLoadout(SkinChroma):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinChromaPayload, parent: Skin) -> None:
        super().__init__(state=state, data=data, parent=parent)


class SkinLevelLoadout(SkinLevel):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinLevelPayload, parent: Skin, level_number: int) -> None:
        super().__init__(state=state, data=data, parent=parent, level_number=level_number)


class Gun(Weapon):
    def __init__(
        self,
        state: CacheState,
        data: ValorantAPIWeaponPayload,
        data_loadout: GunPayload,
        *,
        favorites: Optional[Favorites] = None,
    ) -> None:
        super().__init__(state=state, data=data)
        self.data_loadout = data_loadout
        self._skin_loadout: Optional[Union[Skin, SkinLevel, SkinChroma]] = None
        self._buddy_loadout: Optional[Buddy] = None
        self._buddy_level_loadout: Optional[BuddyLevel] = None

        # skin loadout
        if data_loadout.get('ChromaID'):
            self._skin_loadout = state.get_skin_chroma(data_loadout['ChromaID'])  # type: ignore
        elif data_loadout.get('SkinLevelID'):
            self._skin_loadout = state.get_skin_level(data_loadout['SkinLevelID'])
        elif data_loadout.get('SkinID'):
            self._skin_loadout = state.get_skin(data_loadout['SkinID'])  # type: ignore
        if self._skin_loadout is None:
            _log.warning('could not find skin for gun %r', self.uuid)

        # buddy loadout
        if data_loadout.get('CharmID'):
            self._buddy_loadout = state.get_buddy(uuid=self.data_loadout.get('CharmID'))
            if self._buddy_loadout is None:
                _log.warning('could not find buddy for gun %r', self.uuid)

        if data_loadout.get('CharmLevelID'):
            self._buddy_level_loadout = state.get_buddy_level(uuid=self.data_loadout.get('CharmLevelID'))
            if self._buddy_level_loadout is None:
                _log.warning('could not find buddy level for gun %r', self.uuid)

    @property
    def skin_loadout(self) -> Optional[Union[Skin, SkinLevel, SkinChroma]]:
        return self._skin_loadout

    @property
    def buddy_loadout(self) -> Optional[Buddy]:
        """Returns the get_buddy for this skin"""
        return self._buddy_loadout

    @property
    def charm(self) -> Optional[Buddy]:
        """Returns the get_buddy for this skin"""
        return self._buddy_loadout

    @property
    def buddy_level_loadout(self) -> Optional[BuddyLevel]:
        """Returns the get_buddy level for this skin"""
        return self._buddy_level_loadout

    @property
    def charm_level(self) -> Optional[BuddyLevel]:
        """Returns the get_buddy level for this skin"""
        return self._buddy_level_loadout

    @classmethod
    def from_loadout(
        cls, *, state: CacheState, data_loadout: GunPayload, favorites: Optional[Favorites] = None
    ) -> Optional[Self]:
        weapon = state.get_weapon(uuid=data_loadout['ID'])
        if weapon is None:
            return None
        return cls(state=state, data=weapon._data, data_loadout=data_loadout, favorites=favorites)


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

    # async def refresh_account_level(self) -> None:
    #     account_xp = await self._client.fetch_account_xp()


class SprayLoadout:
    def __init__(self, client: Client, data: SprayPayload, *, favorite: bool) -> None:
        self._client: Client = client
        self._favorite: bool = favorite
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

    @property
    def favorite(self) -> bool:
        return self._favorite

    def get_spray(self) -> Optional[Spray]:
        return self._spray

    def get_spray_level(self) -> Optional[SprayLevel]:
        return self._spray_level


class GunsLoadout:
    def __init__(self, state: CacheState, guns: List[GunPayload], favorites: Optional[Favorites] = None) -> None:
        self._state: CacheState = state
        self.melee: Optional[Gun] = None
        self.classic: Optional[Gun] = None
        self.shorty: Optional[Gun] = None
        self.frenzy: Optional[Gun] = None
        self.ghost: Optional[Gun] = None
        self.sheriff: Optional[Gun] = None
        self.stinger: Optional[Gun] = None
        self.spectre: Optional[Gun] = None
        self.bucky: Optional[Gun] = None
        self.judge: Optional[Gun] = None
        self.bulldog: Optional[Gun] = None
        self.guardian: Optional[Gun] = None
        self.phantom: Optional[Gun] = None
        self.vandal: Optional[Gun] = None
        self.marshal: Optional[Gun] = None
        self.operator: Optional[Gun] = None
        self.ares: Optional[Gun] = None
        self.odin: Optional[Gun] = None

        for data in guns:
            gun = Gun.from_loadout(state=state, data_loadout=data, favorites=favorites)
            if gun is None:
                _log.warning('could not find gun for loadout %r', data)
                continue
            attrname = gun.display_name.default.lower()
            if hasattr(self, attrname):
                setattr(self, attrname, gun)
            else:
                _log.warning('could not find attribute for gun %r', gun)

    def __repr__(self) -> str:
        attrs = [
            ('classic', self.classic),
            ('shorty', self.shorty),
            ('frenzy', self.frenzy),
            ('ghost', self.ghost),
            ('sheriff', self.sheriff),
            ('stinger', self.stinger),
            ('spectre', self.spectre),
            ('bucky', self.bucky),
            ('judge', self.judge),
            ('bulldog', self.bulldog),
            ('guardian', self.guardian),
            ('phantom', self.phantom),
            ('vandal', self.vandal),
            ('marshal', self.marshal),
            ('operator', self.operator),
            ('ares', self.ares),
            ('odin', self.odin),
            ('melee', self.melee),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __iter__(self) -> Iterator[Optional[Gun]]:
        skin_l = [self.melee, *self.sidearms, *self.smgs, *self.shotguns, *self.rifles, *self.snipers, *self.machine_guns]
        return iter(skin_l)

    @property
    def sidearms(self) -> List[Optional[Gun]]:
        return [
            self.classic,
            self.shorty,
            self.frenzy,
            self.ghost,
            self.sheriff,
        ]

    @property
    def smgs(self) -> List[Optional[Gun]]:
        return [self.stinger, self.spectre]

    @property
    def shotguns(self) -> List[Optional[Gun]]:
        return [self.bucky, self.judge]

    @property
    def rifles(self) -> List[Optional[Gun]]:
        return [self.bulldog, self.guardian, self.phantom, self.vandal]

    @property
    def snipers(self) -> List[Optional[Gun]]:
        return [self.marshal, self.operator]

    @property
    def machine_guns(self) -> List[Optional[Gun]]:
        return [self.ares, self.odin]

    def to_list(self) -> List[Optional[Gun]]:
        return [self.melee, *self.sidearms, *self.smgs, *self.shotguns, *self.rifles, *self.snipers, *self.machine_guns]


class Loadout:
    def __init__(self, client: Client, data: LoadoutPayload, favorites: Optional[Favorites] = None) -> None:
        self._client: Client = client
        self.subject: str = data['Subject']
        self.version: int = data['Version']
        self.guns: GunsLoadout = GunsLoadout(client.valorant_api.cache, data['Guns'], favorites=favorites)
        # for gun_data in data['Guns']:
        #     gun = Gun.from_loadout(state=client.valorant_api.cache, data_loadout=gun_data)
        # if gun is None:
        #     _log.warning('could not find gun for loadout %r', data)
        #     continue
        # attrname = gun.display_name.default.lower()
        # if hasattr(self, attrname):
        #     setattr(self, attrname, gun)
        # else:
        #     _log.warning('could not find attribute for gun %r', gun)

        self._sprays: Dict[str, SprayLoadout] = {}
        self.identity: Identity = Identity(self._client, data['Identity'])
        self.incognito: bool = data['Incognito']
        for spray in data['Sprays']:
            spray_loadout = SprayLoadout(self._client, spray, favorite=False)
            self._sprays[str(spray_loadout.slot_number)] = spray_loadout
        self.favorites: Optional[Favorites] = None

    def __repr__(self) -> str:
        return f'<Loadout subject={self.subject!r} version={self.version}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Loadout) and (self.version == other.version or self.incognito == other.incognito)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.subject, self.version, self.incognito))

    @property
    def sprays(self) -> List[SprayLoadout]:
        return list(self._sprays.values())

    def get_spray(self, slot_number: Literal[0, 1, 2]) -> Optional[SprayLoadout]:
        return self._sprays.get(str(slot_number))

    #     account_xp = await self._client.fetch_account_xp()
    #     self._client.user.account_level = account_xp.level
    #     self.identity.account_level = account_xp.level

    async def _update_favorites(self):
        ...
        # self.favorites = await self._client.fetch_favorites()

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
