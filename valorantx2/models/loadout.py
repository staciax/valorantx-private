from __future__ import annotations

import logging

# TODO: loadoutbuilder
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Literal, Optional, Union

from ..enums import LevelBorderID, SpraySlotID
from .weapons import Skin, SkinChroma, SkinLevel, Weapon

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx2.valorant_api.types.weapons import (
        Skin as ValorantAPISkinPayload,
        SkinChroma as ValorantAPISkinChromaPayload,
        SkinLevel as ValorantAPISkinLevelPayload,
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


class _GunLoadout:
    _state: CacheState

    def loadout_init(self, data: GunPayload) -> None:
        self._loadout_buddy_uuid = data.get('CharmID')
        self._loadout_buddy_level_uuid = data.get('CharmLevelID')
        self._is_random: bool = False
        self._loadout_buddy: Optional[Buddy] = None
        self._loadout_buddy_level: Optional[BuddyLevel] = None
        self.attachments: List[Any] = data['Attachments']

        if self._loadout_buddy_uuid is None:
            self._loadout_buddy = self._state.get_buddy(uuid=self._loadout_buddy_uuid)
        if self._loadout_buddy_level_uuid is None:
            self._loadout_buddy_level = self._state.get_buddy_level(uuid=self._loadout_buddy_level_uuid)

        if hasattr(self, 'asset_path'):
            self._is_random = 'Random' in getattr(self, 'asset_path')

    def is_random(self) -> bool:
        """:class:`bool` Returns whether the skin is random."""
        return self._is_random

    @property
    def buddy(self) -> Optional[Buddy]:
        """Returns the get_buddy for this skin"""
        return self._loadout_buddy

    @property
    def charm(self) -> Optional[Buddy]:
        """Returns the get_buddy for this skin"""
        return self._loadout_buddy

    @property
    def buddy_level(self) -> Optional[BuddyLevel]:
        """Returns the get_buddy level for this skin"""
        return self._loadout_buddy_level

    @property
    def charm_level(self) -> Optional[BuddyLevel]:
        """Returns the get_buddy level for this skin"""
        return self._loadout_buddy_level

    # def is_favorite(self) -> bool:
    #     """Returns whether the skin is favorited"""
    #     return self._is_favorite


class SkinLoadout(Skin, _GunLoadout):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinPayload, parent: Weapon, loadout: GunPayload) -> None:
        super().__init__(state=state, data=data, parent=parent)
        self.chromas: List[SkinChromaLoadout] = [
            SkinChromaLoadout(state=state, data=chroma, parent=self, loadout=loadout) for chroma in data['chromas']
        ]
        self.levels: List[SkinLevelLoadout] = [
            SkinLevelLoadout(state=state, data=level, parent=self, level_number=index, loadout=loadout)
            for index, level in enumerate(data['levels'])
        ]
        self.loadout_init(data=loadout)

    def __repr__(self) -> str:
        return f'<SkinLoadout display_name={self.display_name!r}>'

    @classmethod
    def from_loadout(cls, *, state: CacheState, uuid: str, loadout: GunPayload) -> Optional[Self]:
        skin = state.get_skin(uuid=uuid)
        if skin is None:
            return None
        return cls(state=state, data=skin._data, parent=skin.parent, loadout=loadout)


class SkinLevelLoadout(SkinLevel, _GunLoadout):
    def __init__(
        self,
        *,
        state: CacheState,
        data: ValorantAPISkinLevelPayload,
        parent: Union[Skin, SkinLoadout],
        level_number: int,
        loadout: GunPayload,
    ) -> None:
        super().__init__(state=state, data=data, parent=parent, level_number=level_number)
        self.loadout_init(data=loadout)

    def __repr__(self) -> str:
        return f'<SkinLevelLoadout display_name={self.display_name!r}>'

    @classmethod
    def from_loadout(cls, *, state: CacheState, uuid: str, loadout: GunPayload) -> Optional[Self]:
        skin_level = state.get_skin_level(uuid=uuid)
        if skin_level is None:
            return None
        return cls(
            state=state,
            data=skin_level._data,
            parent=skin_level.parent,
            level_number=skin_level.level_number,
            loadout=loadout,
        )


class SkinChromaLoadout(SkinChroma, _GunLoadout):
    def __init__(
        self, *, state: CacheState, data: ValorantAPISkinChromaPayload, parent: Union[Skin, SkinLoadout], loadout: GunPayload
    ) -> None:
        super().__init__(state=state, data=data, parent=parent)
        self.loadout_init(data=loadout)

    def __repr__(self) -> str:
        return f'<SkinChromaLoadout display_name={self.display_name!r}>'

    @classmethod
    def from_loadout(cls, *, state: CacheState, uuid: str, loadout: GunPayload) -> Optional[Self]:
        skin_chroma = state.get_skin_chroma(uuid=uuid)
        if skin_chroma is None:
            return None
        return cls(
            state=state,
            data=skin_chroma._data,
            parent=skin_chroma.parent,
            loadout=loadout,
        )


SkinL = Union[SkinLoadout, SkinLevelLoadout, SkinChromaLoadout]


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


class GunLoadouts:
    def __init__(self, state: CacheState, guns: List[GunPayload]) -> None:
        self._state: CacheState = state
        self.melee: Optional[SkinL] = None
        self.classic: Optional[SkinL] = None
        self.shorty: Optional[SkinL] = None
        self.frenzy: Optional[SkinL] = None
        self.ghost: Optional[SkinL] = None
        self.sheriff: Optional[SkinL] = None
        self.stinger: Optional[SkinL] = None
        self.spectre: Optional[SkinL] = None
        self.bucky: Optional[SkinL] = None
        self.judge: Optional[SkinL] = None
        self.bulldog: Optional[SkinL] = None
        self.guardian: Optional[SkinL] = None
        self.phantom: Optional[SkinL] = None
        self.vandal: Optional[SkinL] = None
        self.marshal: Optional[SkinL] = None
        self.operator: Optional[SkinL] = None
        self.ares: Optional[SkinL] = None
        self.odin: Optional[SkinL] = None

        for gun in guns:
            parent: Optional[Weapon] = state.get_weapon(gun['ID'])
            skin: Optional[SkinL] = None
            if gun.get('ChromaID'):
                skin = SkinChromaLoadout.from_loadout(state=state, uuid=gun['ChromaID'], loadout=gun)
            elif gun.get('SkinLevelID'):
                skin = SkinLevelLoadout.from_loadout(state=state, uuid=gun['SkinLevelID'], loadout=gun)
            elif gun.get('SkinID'):
                skin = SkinLoadout.from_loadout(state=state, uuid=gun['SkinID'], loadout=gun)
            if skin is None:
                _log.warning('could not find skin for gun %r', gun)
                continue
            if parent is None:
                _log.warning('could not find parent for gun %r', gun)
                continue
            attrname = parent.display_name.default.lower()
            if hasattr(self, attrname):
                setattr(self, attrname, skin)
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

    def __iter__(self) -> Iterator[Optional[SkinL]]:
        skin_l = [self.melee, *self.sidearms, *self.smgs, *self.shotguns, *self.rifles, *self.snipers, *self.machine_guns]
        return iter(skin_l)

    @property
    def sidearms(self) -> List[Optional[SkinL]]:
        return [
            self.classic,
            self.shorty,
            self.frenzy,
            self.ghost,
            self.sheriff,
        ]

    @property
    def smgs(self) -> List[Optional[SkinL]]:
        return [self.stinger, self.spectre]

    @property
    def shotguns(self) -> List[Optional[SkinL]]:
        return [self.bucky, self.judge]

    @property
    def rifles(self) -> List[Optional[SkinL]]:
        return [self.bulldog, self.guardian, self.phantom, self.vandal]

    @property
    def snipers(self) -> List[Optional[SkinL]]:
        return [self.marshal, self.operator]

    @property
    def machine_guns(self) -> List[Optional[SkinL]]:
        return [self.ares, self.odin]

    def to_list(self) -> List[Optional[SkinL]]:
        return [self.melee, *self.sidearms, *self.smgs, *self.shotguns, *self.rifles, *self.snipers, *self.machine_guns]


class Loadout:
    def __init__(self, client: Client, data: LoadoutPayload) -> None:
        self._client: Client = client
        self.subject: str = data['Subject']
        self.version: int = data['Version']
        self.guns: GunLoadouts = GunLoadouts(client.valorant_api.cache, data['Guns'])
        self._sprays: Dict[str, SprayLoadout] = {}
        self.identity: Identity = Identity(self._client, data['Identity'])
        self.incognito: bool = data['Incognito']
        for spray in data['Sprays']:
            spray_loadout = SprayLoadout(self._client, spray)
            self._sprays[str(spray_loadout.slot_number)] = spray_loadout

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
        favorites = await self._client.fetch_favorites()

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
