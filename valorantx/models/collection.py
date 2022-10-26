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

import logging
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union

from ..enums import EmptyTitleID, ItemType
from .base import BaseModel
from .spray import SprayLevelLoadout, SprayLoadout
from .weapons import SkinChromaLoadout, SkinLevelLoadout, SkinLoadout

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

    from ..client import Client
    from ..types.collection import (
        Favorites as FavoritesPayload,
        Loadout as LoadoutPayload,
        SkinLoadout as SkinLoadoutPayload,
        SprayLoadout as SprayLoadoutPayload,
    )
    from .buddy import Buddy
    from .level_border import LevelBorder
    from .player import ClientPlayer
    from .player_card import PlayerCard
    from .player_title import PlayerTitle
    from .spray import Spray
    from .weapons import Skin

    SprayL: TypeAlias = Union[SprayLoadout, SprayLevelLoadout]
    SkinL: TypeAlias = Union[SkinLoadout, SkinLevelLoadout, SkinChromaLoadout]

__all__ = (
    'Collection',
    'Favorites',
    'SkinCollection',
    'SprayCollection',
)

_log = logging.getLogger(__name__)


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
        self.user: ClientPlayer = client.user
        self._uuid: str = data['Subject']
        self.version: int = data['Version']
        self._incognito: bool = data.get('Incognito', False)
        self.identity: Identity = Identity(client, data['Identity'])
        self._skins_loadout: List[SkinLoadoutPayload] = data['Guns']
        self._sprays_loadout: List[SprayLoadoutPayload] = data['Sprays']
        self._skins: SkinCollection = SkinCollection()
        self._sprays: SprayCollection = SprayCollection()
        self._update()

    def __repr__(self) -> str:
        return f'<Loadout skins={self.get_skins()!r} version={self.version!r} incognito={self.incognito()!r}>'

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

    def _update(self) -> None:
        spray_loadout = []
        for spray in self._sprays_loadout:
            if spray.get('SprayLevelID'):
                spray_loadout.append(
                    SprayLevelLoadout._from_loadout(client=self._client, uuid=spray['SprayLevelID'], loadout=spray)
                )
            elif spray.get('SprayID'):
                spray_loadout.append(SprayLoadout._from_loadout(client=self._client, uuid=spray['SprayID'], loadout=spray))

        self._sprays._update(spray_loadout)

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

        self._skins._update(skin_loadout)

    def get_sprays(self) -> SprayCollection:
        return self._sprays

    def get_skins(self) -> SkinCollection:
        return self._skins

    # @property
    # def player_name(self) -> str:
    #     return self._client.user.name


class SkinCollection:
    def __init__(self) -> None:
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
    def __init__(self) -> None:
        self._slot_1: Optional[SprayL] = None
        self._slot_2: Optional[SprayL] = None
        self._slot_3: Optional[SprayL] = None

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


class Favorites:
    def __init__(self, *, client: Client, data: FavoritesPayload) -> None:
        self._client = client
        self._data = data
        self._subject: str = data.get('Subject', '')
        self.skins: List[Skin] = []
        self.sprays: List[Spray] = []
        self.player_cards: List[PlayerCard] = []
        self.buddies: List[Buddy] = []
        self.any: List[Any] = []
        self.items: List[Union[Skin, Spray, PlayerCard]] = []
        self._update(data)

    def __repr__(self) -> str:
        attrs = [
            ('len(skins)', len(self.skins)),
            ('len(sprays)', len(self.sprays)),
            ('len(player_cards)', len(self.player_cards)),
            ('len(buddies)', len(self.buddies)),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Favorites)
            and self.skins == other.skins
            and self.sprays == other.sprays
            and self.player_cards == other.player_cards
            and self.buddies == other.buddies
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def _update(self, data: FavoritesPayload) -> None:
        for i in data['FavoritedContent']:
            item_id = data['FavoritedContent'][i]['ItemID']
            item = (
                self._client.get_skin(uuid=item_id, level=False, chroma=False)
                or self._client.get_spray(uuid=item_id, level=False)
                or self._client.get_player_card(uuid=item_id)
                or self._client.get_buddy(uuid=item_id)
            )
            if item is not None:

                if hasattr(item, '_is_favorite'):  # set favorite to True
                    item._is_favorite = True

                if getattr(item, 'type') == ItemType.skin:
                    self.skins.append(item)
                elif getattr(item, 'type') == ItemType.spray:
                    self.sprays.append(item)
                elif getattr(item, 'type') == ItemType.player_card:
                    self.player_cards.append(item)
                elif getattr(item, 'type') == ItemType.buddy:
                    self.buddies.append(item)
                else:
                    _log.warning(f'Unknown item: {item}')
                    self.any.append(item)
                self.items.append(item)

    async def add_skin(self, skin: Union[str, Skin], *, force: bool = False) -> None:
        """|coro|

        Adds a skin to your favorites.

        Parameters
        ----------
        skin: Union[:class:`str`, :class:`Skin`]
            The skin to add.
        force: :class:`bool`
            Whether to force add the skin to your favorites.
        """
        if isinstance(skin, str):
            skin = self._client.get_skin(uuid=skin, level=False, chroma=False)
        if skin in self.skins:
            raise ValueError(f'{skin} is already in your favorites.')

        is_favorite = await skin.add_favorite(force=force)
        if is_favorite:
            self.skins.append(skin)

    async def add_spray(self, spray: Union[str, Spray], *, force: bool = False) -> None:
        """|coro|

        Adds a spray to your favorites.

        Parameters
        ----------
        spray: Union[:class:`str`, :class:`Spray`]
            The spray to add.
        force: :class:`bool`
            Whether to force add the spray to your favorites.
        """
        if isinstance(spray, str):
            spray = self._client.get_spray(uuid=spray, level=False)
        if spray in self.sprays:
            raise ValueError(f'{spray} is already in your favorites.')

        is_favorite = await spray.add_favorite(force=force)
        if is_favorite:
            self.sprays.append(spray)

    async def add_player_card(self, player_card: Union[str, PlayerCard], *, force: bool = False) -> None:
        """|coro|

        Adds a player card to your favorites.

        Parameters
        ----------
        player_card: Union[:class:`str`, :class:`PlayerCard`]
            The player card to add.
        force: :class:`bool`
            Whether to force add the player card to your favorites.
        """
        if isinstance(player_card, str):
            player_card = self._client.get_player_card(uuid=player_card)
        if player_card in self.player_cards:
            raise ValueError(f'{player_card} is already in your favorites.')

        is_favorite = await player_card.add_favorite(force=force)
        if is_favorite:
            self.player_cards.append(player_card)

    async def add_buddy(self, buddy: Union[str, Buddy], *, force: bool = False) -> None:
        """|coro|

        Adds a buddy to your favorites.

        Parameters
        ----------
        buddy: Union[:class:`str`, :class:`Buddy`]
            The buddy to add.
        force: :class:`bool`
            Whether to force add the buddy to your favorites.
        """
        if isinstance(buddy, str):
            buddy = self._client.get_buddy(uuid=buddy)
        if buddy in self.buddies:
            raise ValueError(f'{buddy} is already in your favorites.')

        is_favorite = await buddy.add_favorite(force=force)
        if is_favorite:
            self.buddies.append(buddy)

    async def remove_skin(self, skin: Union[str, Skin], *, force: bool = False) -> None:
        """|coro|

        Removes a skin from your favorites.

        Parameters
        ----------
        skin: Union[:class:`str`, :class:`Skin`]
            The skin to remove.
        force: :class:`bool`
            Whether to force remove the skin from your favorites.
        """
        if isinstance(skin, str):
            skin = self._client.get_skin(uuid=skin, level=False, chroma=False)
        if skin not in self.skins:
            raise ValueError(f'{skin} is not in your favorites.')
        is_favorite = await skin.remove_favorite(force=force)
        if not is_favorite:
            self.skins.remove(skin)

    async def remove_spray(self, spray: Union[str, Spray], *, force: bool = False) -> None:
        """|coro|

        Removes a spray from your favorites.

        Parameters
        ----------
        spray: Union[:class:`str`, :class:`Spray`]
            The spray to remove.
        force: :class:`bool`
            Whether to force remove the spray from your favorites.
        """
        if isinstance(spray, str):
            spray = self._client.get_spray(uuid=spray, level=False)
        if spray not in self.sprays:
            raise ValueError(f'{spray} is not in your favorites.')
        is_favorite = await spray.remove_favorite(force=force)
        if not is_favorite:
            self.sprays.remove(spray)

    async def remove_player_card(self, player_card: Union[str, PlayerCard], *, force: bool = False) -> None:
        """|coro|

        Removes a player card from your favorites.

        Parameters
        ----------
        player_card: Union[:class:`str`, :class:`PlayerCard`]
            The player card to remove.
        force: :class:`bool`
            Whether to force remove the player card from your favorites.
        """
        if isinstance(player_card, str):
            player_card = self._client.get_player_card(uuid=player_card)
        if player_card not in self.player_cards:
            raise ValueError(f'{player_card} is not in your favorites.')
        is_favorite = await player_card.remove_favorite(force=force)
        if not is_favorite:
            self.player_cards.remove(player_card)

    async def remove_buddy(self, buddy: Union[str, Buddy], *, force: bool = False) -> None:
        """|coro|

        Removes a buddy from your favorites.

        Parameters
        ----------
        buddy: Union[:class:`str`, :class:`Buddy`]
            The buddy to remove.
        force: :class:`bool`
            Whether to force remove the buddy from your favorites.
        """
        if isinstance(buddy, str):
            buddy = self._client.get_buddy(uuid=buddy)
        if buddy not in self.buddies:
            raise ValueError(f'{buddy} is not in your favorites.')
        is_favorite = await buddy.remove_favorite(force=force)
        if not is_favorite:
            self.buddies.remove(buddy)

    async def remove_all(self, item_type: Optional[ItemType] = None, *, force: bool = False) -> None:
        """|coro|

        Removes all items from your favorites.

        Parameters
        ----------
        item_type: Optional[:class:`ItemType`]
            The item type to remove.
        force: :class:`bool`
            Whether to force remove the items from your favorites.
        """

        async def remove_skin() -> None:
            for skin in self.skins:
                is_fav = await skin.remove_favorite(force=force)
                if not is_fav:
                    self.skins.remove(skin)

        async def remove_spray() -> None:
            for spray in self.sprays:
                is_fav = await spray.remove_favorite(force=force)
                if not is_fav:
                    self.sprays.remove(spray)

        async def remove_player_card() -> None:
            for player_card in self.player_cards:
                is_fav = await player_card.remove_favorite(force=force)
                if not is_fav:
                    self.player_cards.remove(player_card)

        async def remove_buddy() -> None:
            for buddy in self.buddies:
                is_fav = await buddy.remove_favorite(force=force)
                if not is_fav:
                    self.buddies.remove(buddy)

        if item_type is None:
            await remove_skin()
            await remove_spray()
            await remove_player_card()
            await remove_buddy()
        elif item_type == ItemType.skin:
            await remove_skin()
        elif item_type == ItemType.spray:
            await remove_spray()
        elif item_type == ItemType.player_card:
            await remove_player_card()
        elif item_type == ItemType.buddy:
            await remove_buddy()
        else:
            raise ValueError(f'Unknown item type: {item_type}')
