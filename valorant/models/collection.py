# from __future__ import annotations
#
# from typing import Optional, List, Dict, Any, TYPE_CHECKING
#
# from ..enums import WeaponID
#
# from .player_card import PlayerCard
# from .player_title import PlayerTitle
# from .level_border import LevelBorder
# # from .other import LevelBorder
# # from .spray import SprayLoadout, SprayCollection
# # from .skin import SkinLoadout
#
# if TYPE_CHECKING:
#     from ..client import Client
#
# __all__ = ('Collection', 'SkinCollection')
#
#
# class Collection:
#
#     """
#     Player Loadout Collection
#
#     .. container:: operations
#
#         .. describe:: x == y
#
#             Checks if two players are equal.
#
#         .. describe:: x != y
#
#             Checks if two players are not equal.
#
#         .. describe:: str(x)
#
#             Returns a string representation of the player.
#
#     Attributes:
#     ___________
#     uuid: :class:`str`
#         The UUID of player.
#     version: :class:`int`
#         The version of player loadout.
#     incognito: :class:`bool`
#         Whether the player is incognito.
#     """
#
#     def __init__(self, client: Client, data: Any) -> None:
#         self._client = client
#         # self.user = client.user
#         self.uuid: str = data['Subject']
#         self.version: int = data['Version']
#         self.incognito: bool = data['Incognito']
#         self._identity: Dict[str, Any] = data['Identity']
#         self._skins_loadout: str = data['Guns']
#         self._sprays_loadout: str = data['Sprays']
#         self._player_card_uuid: str = self._identity['PlayerCardID']
#         self._player_title_uuid: str = self._identity['PlayerTitleID']
#         self._level_border_uuid: str = self._identity['PreferredLevelBorderID']
#
#     # def _update(self, data: Any) -> None:
#     #     self._version: int = data['Version']
#     #     self._incognito: bool = data['Incognito']
#     #     self._identity: Dict[str, Any] = data['Identity']
#     #     self._skins_loadout: str = data['Guns']
#     #     self._sprays_loadout: str = data['Sprays']
#     #     self._player_card_uuid: str = self._identity['PlayerCardID']
#     #     self._player_title_uuid: str = self._identity['PlayerTitleID']
#     #     self._level_border_uuid: str = self._identity['PreferredLevelBorderID']
#
#     def __repr__(self) -> str:
#         return f'<Collection uuid={self.uuid!r} version={self.version!r} incognito={self.incognito!r}>'
#
#     def __eq__(self, other: object) -> bool:
#         return isinstance(other, Collection) and (self.version == other.version or self.incognito == other.incognito)
#
#     def __ne__(self, other: object) -> bool:
#         return not self.__eq__(other)
#
#     def __hash__(self) -> int:
#         return hash((self.uuid, self.version, self.incognito))
#
#     @property
#     def skins(self) -> SkinCollection:
#         return SkinCollection([
#             SkinLoadout._from_uuid(client=self._client, uuid=skin['ChromaID'], extra=skin) for skin in
#             sorted(self._skins_loadout, key=lambda x: x['ID'])
#         ])
#
#     @property
#     def sprays(self) -> SprayCollection:
#         return SprayCollection([
#             SprayLoadout._from_uuid(client=self._client, uuid=spray['SprayID'], extra=spray) for spray in
#             self._sprays_loadout
#         ])
#
#     # @property
#     # def level(self) -> int:
#     #     return self._client.user.account_level
#
#     @property
#     def level_border(self) -> Optional[LevelBorder]:
#         if self._level_border_uuid == '00000000-0000-0000-0000-000000000000':
#             self._level_border_uuid = 'ebc736cd-4b6a-137b-e2b0-1486e31312c9'
#         return LevelBorder._from_uuid(client=self._client, uuid=self._level_border_uuid)
#
#     @property
#     def player_card(self) -> PlayerTitle:
#         return PlayerCard._from_uuid(client=self._client, uuid=self._player_card_uuid)
#
#     @property
#     def player_title(self) -> PlayerTitle:
#         return PlayerTitle._from_uuid(client=self._client, uuid=self._player_title_uuid)
#
#     # @property
#     # def player_name(self) -> str:
#     #     return self._client.user.name
#
#
# class SkinCollection:
#
#     def __init__(self, loadout: List[SkinLoadout]) -> None:
#         self._update(loadout)
#
#     def _update(self, loadout: List[SkinLoadout]) -> None:
#         for skin in loadout:
#             match skin.weapon_id:
#                 case WeaponID.vandal.value:
#                     self._vandal_loadout = skin
#                 case WeaponID.odin.value:
#                     self._odin_loadout = skin
#                 case WeaponID.ares.value:
#                     self._ares_loadout = skin
#                 case WeaponID.bulldog.value:
#                     self._bulldog_loadout = skin
#                 case WeaponID.phantom.value:
#                     self._phantom_loadout = skin
#                 case WeaponID.judge.value:
#                     self._judge_loadout = skin
#                 case WeaponID.bucky.value:
#                     self._bucky_loadout = skin
#                 case WeaponID.frenzy.value:
#                     self._frenzy_loadout = skin
#                 case WeaponID.classic.value:
#                     self._classic_loadout = skin
#                 case WeaponID.ghost.value:
#                     self._ghost_loadout = skin
#                 case WeaponID.sheriff.value:
#                     self._sheriff_loadout = skin
#                 case WeaponID.shorty.value:
#                     self._shorty_loadout = skin
#                 case WeaponID.operator.value:
#                     self._operator_loadout = skin
#                 case WeaponID.guardian.value:
#                     self._guardian_loadout = skin
#                 case WeaponID.marshal.value:
#                     self._marshal_loadout = skin
#                 case WeaponID.spectre.value:
#                     self._spectre_loadout = skin
#                 case WeaponID.stinger.value:
#                     self._stinger_loadout = skin
#                 case WeaponID.melee.value:
#                     self._melee_loadout = skin
#
#     @property
#     def melee(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the melee loadout."""
#         return self._melee_loadout
#
#     @property
#     def classic(self) -> SkinLoadout:
#         """ :class:`SkinLoadout` Returns the classic loadout."""
#         return self._classic_loadout
#
#     @property
#     def shorty(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the shorty loadout."""
#         return self._shorty_loadout
#
#     @property
#     def frenzy(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the frenzy loadout."""
#         return self._frenzy_loadout
#
#     @property
#     def ghost(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the ghost loadout."""
#         return self._ghost_loadout
#
#     @property
#     def sheriff(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the sheriff loadout."""
#         return self._sheriff_loadout
#
#     @property
#     def stinger(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the stinger loadout."""
#         return self._stinger_loadout
#
#     @property
#     def spectre(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the spectre loadout."""
#         return self._spectre_loadout
#
#     @property
#     def bucky(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the bucky loadout."""
#         return self._bucky_loadout
#
#     @property
#     def judge(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the judge loadout."""
#         return self._judge_loadout
#
#     @property
#     def bulldog(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the bulldog loadout."""
#         return self._bulldog_loadout
#
#     @property
#     def guardian(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the guardian loadout."""
#         return self._guardian_loadout
#
#     @property
#     def phantom(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the phantom loadout."""
#         return self._phantom_loadout
#
#     @property
#     def vandal(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the vandal loadout."""
#         return self._vandal_loadout
#
#     @property
#     def marshal(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the marshal loadout."""
#         return self._marshal_loadout
#
#     @property
#     def operator(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the operator loadout."""
#         return self._operator_loadout
#
#     @property
#     def ares(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the ares loadout."""
#         return self._ares_loadout
#
#     @property
#     def odin(self) -> SkinLoadout:
#         """:class:`SkinLoadout` Returns the odin loadout."""
#         return self._odin_loadout
#
#     @property
#     def sidearms(self) -> List[SkinLoadout]:
#         return [
#             self.classic,
#             self.shorty,
#             self.frenzy,
#             self.ghost,
#             self.sheriff,
#         ]
#
#     @property
#     def smgs(self) -> List[SkinLoadout]:
#         return [
#             self.stinger,
#             self.spectre
#         ]
#
#     @property
#     def shotguns(self) -> List[SkinLoadout]:
#         return [
#             self.bucky,
#             self.judge
#         ]
#
#     @property
#     def rifles(self) -> List[SkinLoadout]:
#         return [
#             self.bulldog,
#             self.guardian,
#             self.phantom,
#             self.vandal
#         ]
#
#     @property
#     def snipers(self) -> List[SkinLoadout]:
#         return [
#             self.marshal,
#             self.operator
#         ]
#
#     @property
#     def machine_guns(self) -> List[SkinLoadout]:
#         return [
#             self.ares,
#             self.odin
#         ]
#
#     def to_list(self) -> List[SkinLoadout]:
#         return [
#             self.melee,
#             *self.sidearms,
#             *self.smgs,
#             *self.shotguns,
#             *self.rifles,
#             *self.snipers,
#             *self.machine_guns
#         ]
