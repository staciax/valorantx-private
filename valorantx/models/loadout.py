from __future__ import annotations

import logging

# TODO: loadoutbuilder
from typing import TYPE_CHECKING, Iterator, List, Optional, Union

from valorantx.models.weapons import Weapon
from valorantx.valorant_api_cache import CacheState

from ..enums import LevelBorderID, SpraySlotID
from .weapons import Weapon

if TYPE_CHECKING:
    from typing_extensions import Self

    from valorantx.valorant_api.types.weapons import Weapon as ValorantAPIWeaponPayload

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
    from .sprays import Spray
    from .weapons import Skin, SkinChroma, SkinLevel


_log = logging.getLogger(__name__)

__all__ = (
    'Loadout',
    'Identity',
)


class Gun(Weapon):
    def __init__(
        self,
        state: CacheState,
        data: ValorantAPIWeaponPayload,
        data_loadout: GunPayload,
        favorites: Favorites,
    ) -> None:
        super().__init__(state=state, data=data)
        self.data_loadout = data_loadout
        self.favorites = favorites
        self._skin_loadout: Optional[Union[Skin, SkinLevel, SkinChroma]] = None
        self._buddy_loadout: Optional[Buddy] = None
        self._buddy_level_loadout: Optional[BuddyLevel] = None

        # skin loadout
        if data_loadout.get('ChromaID'):
            skin_chroma = state.get_skin_chroma(data_loadout['ChromaID'])
            if skin_chroma is not None:
                self._skin_loadout = skin_chroma.__class__.from_loadout(
                    skin_chroma=skin_chroma, favorite=skin_chroma.uuid in favorites.favorited_content
                )
            else:
                _log.warning('could not find skin chroma for gun %r', self.uuid)
        elif data_loadout.get('SkinLevelID'):
            skin_level = state.get_skin_level(data_loadout['SkinLevelID'])
            if skin_level is not None:
                self._skin_loadout = skin_level.__class__.from_loadout(
                    skin_level=skin_level, favorite=skin_level.uuid in favorites.favorited_content
                )
            else:
                _log.warning('could not find skin level for gun %r', self.uuid)
        elif data_loadout.get('SkinID'):
            skin = state.get_skin(data_loadout['SkinID'])
            if skin is not None:
                self._skin_loadout = skin.__class__.from_loadout(
                    skin=skin, favorite=skin.uuid in favorites.favorited_content
                )
            else:
                _log.warning('could not find skin for gun %r', self.uuid)

        # buddy loadout
        if data_loadout.get('CharmID'):
            buddy = state.get_buddy(uuid=self.data_loadout.get('CharmID'))
            if buddy is not None:
                self._buddy_loadout = buddy.__class__.from_loadout(
                    buddy=buddy, favorite=buddy.uuid in favorites.favorited_content
                )
            else:
                _log.warning('could not find buddy for gun %r', self.uuid)

        if data_loadout.get('CharmLevelID'):
            buddy_level = state.get_buddy_level(uuid=self.data_loadout.get('CharmLevelID'))
            if buddy_level is not None:
                self._buddy_level_loadout = buddy_level._copy(buddy_level=buddy_level)
            else:
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
    def from_loadout(cls, *, weapon: Weapon, data_loadout: GunPayload, favorites: Favorites) -> Self:
        weapon = weapon._copy(weapon=weapon)
        return cls(state=weapon._state, data=weapon._data, data_loadout=data_loadout, favorites=favorites)

    def to_payload(self) -> GunPayload:
        return self.data_loadout


class Identity:
    def __init__(self, client: Client, data: IdentityPayload, favorites: Favorites) -> None:
        self._client = client
        self.favorites = favorites
        self._player_card_id: str = data['PlayerCardID']
        self._player_title_id: str = data['PlayerTitleID']
        self.account_level: int = data['AccountLevel']
        self._preferred_level_border_id: str = data['PreferredLevelBorderID']
        self.hide_account_level: bool = data['HideAccountLevel']
        self._player_card: Optional[PlayerCard] = None
        self._player_title: Optional[PlayerTitle] = None
        self._preferred_level_border: Optional[LevelBorder] = None

        # player card
        player_card = self._client.valorant_api.get_player_card(self._player_card_id)
        if player_card is not None:
            self.player_card = player_card.__class__.from_loadout(
                player_card=player_card, favorite=player_card.uuid in favorites.favorited_content
            )
        else:
            _log.warning(f'player card {self._player_card_id!r} not found')

        # player title
        player_title = self._client.valorant_api.get_player_title(self._player_title_id)
        if player_title is not None:
            self.player_title = player_title.__class__.from_loadout(
                player_title=player_title,
                favorite=player_title.uuid in favorites.favorited_content,  # NOTE: player title not support favorite
            )
        else:
            _log.warning(f'player title {self._player_title_id!r} not found')

        # level border
        if self._preferred_level_border_id != LevelBorderID.empty.value:
            preferred_level_border = self._client.valorant_api.get_level_border(self._preferred_level_border_id)
            if preferred_level_border is not None:
                self.preferred_level_border = preferred_level_border.__class__.from_loadout(
                    level_border=preferred_level_border,
                    favorite=preferred_level_border.uuid in favorites.favorited_content,
                )
            else:
                _log.warning(f'level border {self._preferred_level_border_id!r} not found')

    # def _update_from_data(self, data: IdentityPayload) -> None:
    #     self._player_card_id = data['PlayerCardID']
    #     self._player_title_id = data['PlayerTitleID']
    #     self.account_level = data['AccountLevel']
    #     self._preferred_level_border_id = data['PreferredLevelBorderID']
    #     self.hide_account_level = data['HideAccountLevel']

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

    def to_payload(self) -> IdentityPayload:
        payload: IdentityPayload = {
            'PlayerCardID': self.player_card.uuid if self.player_card is not None else self._player_card_id,
            'PlayerTitleID': self.player_title.uuid if self.player_title is not None else self._player_title_id,
            'AccountLevel': self.account_level,
            'PreferredLevelBorderID': self.preferred_level_border.uuid
            if self.preferred_level_border is not None
            else self._preferred_level_border_id,
            'HideAccountLevel': self.hide_account_level,
        }
        return payload


class GunsLoadout:
    def __init__(self, state: CacheState, guns: List[GunPayload], favorites: Favorites) -> None:
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
            weapon = state.get_weapon(uuid=data['ID'])
            if weapon is None:
                _log.warning('could not find weapon for loadout %r', data)
                continue
            gun = Gun.from_loadout(weapon=weapon, data_loadout=data, favorites=favorites)
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

    def to_payload(self) -> List[GunPayload]:
        payload = []
        for gun in self.to_list():
            if gun is not None:
                payload.append(gun.to_payload())
        return payload


class SpraysLoadout:
    def __init__(self, state: CacheState, sprays: List[SprayPayload], favorites: Favorites) -> None:
        self._sprays: List[SprayPayload] = sprays
        self.slot_1: Optional[Spray] = None
        self.slot_2: Optional[Spray] = None
        self.slot_3: Optional[Spray] = None
        self.slot_4: Optional[Spray] = None  # TODO: patch 6.10 support sprays in 4th slot
        for spray_data in sprays:
            equip_slot_id = spray_data['EquipSlotID']
            spray = state.get_spray(spray_data['SprayID'])
            if spray is None:
                _log.warning('could not find spray for loadout %r', spray_data)
                continue
            spray = spray.from_loadout(spray=spray, favorite=spray.uuid in favorites.favorited_content)
            if equip_slot_id == SpraySlotID.slot_1.value:
                self.slot_1 = spray
            elif equip_slot_id == SpraySlotID.slot_2.value:
                self.slot_2 = spray
            elif equip_slot_id == SpraySlotID.slot_3.value:
                self.slot_3 = spray
            else:
                _log.warning('unknown spray slot %r', spray_data)

    def __repr__(self) -> str:
        attrs = [
            ('slot_1', self.slot_1),
            ('slot_2', self.slot_2),
            ('slot_3', self.slot_3),
            ('slot_4', self.slot_4),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __iter__(self) -> Iterator[Optional[Spray]]:
        return iter([self.slot_1, self.slot_2, self.slot_3, self.slot_4])

    def to_list(self) -> List[Optional[Spray]]:
        return [self.slot_1, self.slot_2, self.slot_3, self.slot_4]

    def to_payload(self) -> List[SprayPayload]:
        # payload = []
        # for spray in self.to_list():
        #     if spray is not None:
        #         payload.append(spray.to_payload())
        return self._sprays


class Loadout:
    def __init__(self, client: Client, data: LoadoutPayload, favorites: Favorites) -> None:
        self._client: Client = client
        self.subject: str = data['Subject']
        self.version: int = data['Version']
        self.guns: GunsLoadout = GunsLoadout(client.valorant_api.cache, data['Guns'], favorites=favorites)
        self.sprays: SpraysLoadout = SpraysLoadout(client.valorant_api.cache, data['Sprays'], favorites=favorites)
        self.identity: Identity = Identity(self._client, data['Identity'], favorites)
        self.incognito: bool = data['Incognito']
        self.favorites: Optional[Favorites] = None

    def __repr__(self) -> str:
        return f'<Loadout subject={self.subject!r} version={self.version}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Loadout) and (self.version == other.version or self.incognito == other.incognito)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.subject, self.version, self.incognito))

    #     account_xp = await self._client.fetch_account_xp()
    #     self._client.user.account_level = account_xp.level
    #     self.identity.account_level = account_xp.level

    def to_payload(self) -> LoadoutPayload:
        payload: LoadoutPayload = {
            'Subject': self.subject,
            'Version': self.version,
            'Guns': self.guns.to_payload(),
            'Sprays': self.sprays.to_payload(),
            'Identity': self.identity.to_payload(),
            'Incognito': self.incognito,
        }
        return payload


# class GunsBuilder:
#     def __init__(
#         self,
#         melee: Optional[Gun] = None,
#         classic: Optional[Gun] = None,
#         shorty: Optional[Gun] = None,
#         frenzy: Optional[Gun] = None,
#         ghost: Optional[Gun] = None,
#         sheriff: Optional[Gun] = None,
#         stinger: Optional[Gun] = None,
#         spectre: Optional[Gun] = None,
#         bucky: Optional[Gun] = None,
#         judge: Optional[Gun] = None,
#         bulldog: Optional[Gun] = None,
#         guardian: Optional[Gun] = None,
#         phantom: Optional[Gun] = None,
#         vandal: Optional[Gun] = None,
#         marshal: Optional[Gun] = None,
#         operator: Optional[Gun] = None,
#         ares: Optional[Gun] = None,
#         odin: Optional[Gun] = None,
#     ) -> None:
#         self.melee: Optional[Gun] = melee
#         self.classic: Optional[Gun] = classic
#         self.shorty: Optional[Gun] = shorty
#         self.frenzy: Optional[Gun] = frenzy
#         self.ghost: Optional[Gun] = ghost
#         self.sheriff: Optional[Gun] = sheriff
#         self.stinger: Optional[Gun] = stinger
#         self.spectre: Optional[Gun] = spectre
#         self.bucky: Optional[Gun] = bucky
#         self.judge: Optional[Gun] = judge
#         self.bulldog: Optional[Gun] = bulldog
#         self.guardian: Optional[Gun] = guardian
#         self.phantom: Optional[Gun] = phantom
#         self.vandal: Optional[Gun] = vandal
#         self.marshal: Optional[Gun] = marshal
#         self.operator: Optional[Gun] = operator
#         self.ares: Optional[Gun] = ares
#         self.odin: Optional[Gun] = odin


# class LoadoutBuilder:
#     def __init__(self, client: Client, subject: str, version: int = 0) -> None:
#         self._client: Client = client
#         self.subject: str = subject
#         self.version: int = version

#         self.incognito: bool = False
