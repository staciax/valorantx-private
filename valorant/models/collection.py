"""
The MIT License (MIT)

Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union

from ..enums import EmptyTitleID
from .base import BaseModel
from .spray import SprayLevelLoadout, SprayLoadout
from .weapons import SkinChromaLoadout, SkinLevelLoadout, SkinLoadout

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from ..client import Client
    from ..types.collection import (
        Loadout as LoadoutPayload,
        SkinLoadout as SkinLoadoutPayload,
        SprayLoadout as SprayLoadoutPayload,
    )
    from .level_border import LevelBorder
    from .player_card import PlayerCard
    from .player_title import PlayerTitle

    SprayL: TypeAlias = Union[SprayLoadout, SprayLevelLoadout]
    SkinL: TypeAlias = Union[SkinLoadout, SkinLevelLoadout, SkinChromaLoadout]

__all__ = (
    'Collection',
    'SkinCollection',
    'SprayCollection',
)


class Identity:
    def __init__(self, client: Client, data: Dict[str, Any]) -> None:
        self._client = client
        self._player_card: Optional[str] = data.get('PlayerCardID')
        self._player_title: Optional[str] = data.get('PlayerTitleID')
        self._level_border: Optional[str] = data.get('PreferredLevelBorderID')
        self._account_level: int = 0
        self._hide_account_level: bool = data.get('HideAccountLevel', False)

    def __repr__(self) -> str:
        attrs = [
            ('player_card', self.player_card),
            ('player_title', self.player_title),
            ('level_border', self.level_border),
            ('account_level', self.account_level),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Identity) and (
            self.player_card == other.player_card
            and self.player_title == other.player_title
            and self.level_border == other.level_border
            and self.account_level == other.account_level
            and self._hide_account_level == other._hide_account_level
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def player_card(self) -> Optional[PlayerCard]:
        """:class:`PlayerCard`: The player card."""
        return self._client.get_player_card(self._player_card)

    @property
    def player_title(self) -> Optional[PlayerTitle]:
        """:class:`PlayerTitle`: The player title."""
        if not self._player_title == str(EmptyTitleID):  # TODO: Fix this
            return self._client.get_player_title(self._player_title)
        return None

    @property
    def level_border(self) -> Optional[LevelBorder]:
        """:class:`LevelBorder`: The level border."""
        # return self._client.get_level_border(self._level_border) # v1
        return self._client.get_level_border(self._account_level)

    @property
    def account_level(self) -> int:
        """:class:`int`: The account level."""
        return self._account_level

    @account_level.setter
    def account_level(self, value: int) -> None:
        self._account_level = value

    def hide_account_level(self) -> bool:
        """:class:`bool`: Whether the account level is hidden."""
        return self._hide_account_level


class Collection(BaseModel):

    """
    Player Loadout

    .. container:: operations

        .. describe:: x == y

            Checks if two players are equal.

        .. describe:: x != y

            Checks if two players are not equal.

    Attributes:
    ___________
    uuid: :class:`str`
        The UUID of player.
    version: :class:`int`
        The version of player loadout.
    incognito: :class:`bool`
        Whether the player is incognito.
    """

    def __init__(self, client: Client, data: LoadoutPayload, **kwargs: Any) -> None:
        super().__init__(client, data, **kwargs)
        # self.user = client.user
        self._uuid: str = data['Subject']
        self.version: int = data['Version']
        self._incognito: bool = data.get('Incognito', False)
        self.identity: Identity = Identity(client, data['Identity'])
        self._skins_loadout: List[SkinLoadoutPayload] = data['Guns']
        self._sprays_loadout: List[SprayLoadoutPayload] = data['Sprays']

    def __repr__(self) -> str:
        return f'<Loadout skins={self.skins!r} version={self.version!r} incognito={self.incognito()!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Collection) and (self.version == other.version or self.incognito == other.incognito)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.uuid, self.version, self.incognito))

    def incognito(self) -> bool:
        """
        Whether the player is incognito.
        """
        return self._incognito

    @property
    def sprays(self) -> Union[SprayCollection, List[SprayL]]:
        spray_loadout = []
        for spray in self._sprays_loadout:
            if spray.get('SprayLevelID'):
                spray_loadout.append(
                    SprayLevelLoadout._from_loadout(client=self._client, uuid=spray['SprayLevelID'], loadout=spray)
                )
            elif spray.get('SprayID'):
                spray_loadout.append(SprayLoadout._from_loadout(client=self._client, uuid=spray['SprayID'], loadout=spray))

        return SprayCollection(spray_loadout)

    @property
    def skins(self) -> Union[SkinCollection, List[SkinL]]:

        skin_loadout = []
        for skin in sorted(self._skins_loadout, key=lambda x: x['ID']):
            if skin.get('ChromaID'):
                skin_loadout.append(
                    SkinChromaLoadout._from_loadout(client=self._client, uuid=skin['ChromaID'], loadout=skin)
                )
            elif skin.get('SkinLevelID'):
                skin_loadout.append(
                    SkinLevelLoadout._from_loadout(client=self._client, uuid=skin['SkinLevelID'], loadout=skin)
                )
            elif skin.get('SkinID'):
                skin_loadout.append(SkinLoadout._from_loadout(client=self._client, uuid=skin['SkinID'], loadout=skin))

        return SkinCollection(skin_loadout)

    # @property
    # def player_name(self) -> str:
    #     return self._client.user.name


class SkinCollection:
    def __init__(self, loadout: List[SkinL]) -> None:
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
        self._update(loadout)

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

    def __iter__(self) -> Iterator[SkinL]:
        return iter(
            [self.melee, *self.sidearms, *self.smgs, *self.shotguns, *self.rifles, *self.snipers, *self.machine_guns]
        )

    def _update(self, loadout: List[SkinL]) -> None:
        for skin in loadout:
            if hasattr(self, skin.base_weapon.display_name.lower()):
                setattr(self, skin.base_weapon.display_name.lower(), skin)

    @property
    def sidearms(self) -> List[SkinL]:
        return [
            self.classic,
            self.shorty,
            self.frenzy,
            self.ghost,
            self.sheriff,
        ]

    @property
    def smgs(self) -> List[SkinL]:
        return [self.stinger, self.spectre]

    @property
    def shotguns(self) -> List[SkinL]:
        return [self.bucky, self.judge]

    @property
    def rifles(self) -> List[SkinL]:
        return [self.bulldog, self.guardian, self.phantom, self.vandal]

    @property
    def snipers(self) -> List[SkinL]:
        return [self.marshal, self.operator]

    @property
    def machine_guns(self) -> List[SkinL]:
        return [self.ares, self.odin]

    def to_list(self) -> List[SkinL]:
        return [self.melee, *self.sidearms, *self.smgs, *self.shotguns, *self.rifles, *self.snipers, *self.machine_guns]


class SprayCollection:
    def __init__(self, loadout: List[SprayL]) -> None:
        self._slot_1: Optional[SprayL] = None
        self._slot_2: Optional[SprayL] = None
        self._slot_3: Optional[SprayL] = None
        self._update(loadout)

    def __repr__(self) -> str:
        return f'<SprayCollection slot_1={self.slot_1!r}, slot_2={self.slot_2!r} slot_3={self.slot_3!r}>'

    def __iter__(self) -> Iterator[SprayL]:
        return iter([self.slot_1, self.slot_2, self.slot_3])

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, SprayCollection)
            and self.slot_1 == other.slot_1
            and self.slot_2 == other.slot_2
            and self.slot_3 == other.slot_3
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def _update(self, loadout: List[SprayLoadout]) -> None:
        for spray in loadout:
            if spray.slot_number == 1:
                self._slot_1 = spray
            elif spray.slot_number == 2:
                self._slot_2 = spray
            elif spray.slot_number == 3:
                self._slot_3 = spray

    @property
    def slot_1(self) -> Optional[SprayL]:
        return self._slot_1

    @property
    def slot_2(self) -> Optional[SprayL]:
        return self._slot_2

    @property
    def slot_3(self) -> Optional[SprayL]:
        return self._slot_3

    def to_list(self) -> List[SprayL]:
        return [self.slot_1, self.slot_2, self.slot_3]
