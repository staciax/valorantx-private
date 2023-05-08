from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from ..client import Client
    from ..types.user import PartialUser as PartialUserPayload

# fmt: off
__all__ = (
    'ClientUser',
    'User',
)
# fmt: on


class _BaseUser:
    puuid: str
    __slots__ = ()


class ClientUser(_BaseUser):
    _game_name: Optional[str]
    _tag_line: Optional[str]
    _region: Optional[str]

    def __init__(self, *, data: PartialUserPayload) -> None:
        self._puuid: str = data['puuid']
        self._update(data)

    def __str__(self) -> str:
        return f'{self.game_name}#{self.tag_line}'

    def __repr__(self) -> str:
        return f"<ClientUser puuid={self.puuid!r} game_name={self.game_name!r} tag_line={self.tag_line!r} region={self.region!r}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ClientUser) and other.puuid == self.puuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.puuid)

    def _update(self, data: PartialUserPayload) -> None:
        self._game_name = data.get('game_name')
        self._tagline = data.get('tag_line')
        self._region = data.get('region')

    @property
    def puuid(self) -> str:
        return self._puuid

    @property
    def game_name(self) -> str:
        return self._game_name or ''

    @property
    def tag_line(self) -> str:
        return self._tagline or ''

    @property
    def region(self) -> str:
        return self._region or ''

    @property
    def riot_id(self) -> str:
        return f'{self.game_name}#{self.tag_line}'

    @property
    def display_name(self) -> str:
        return self.riot_id


class User(ClientUser):
    def __init__(self, client: Client, data: Union[PartialUserPayload, Any]) -> None:
        super().__init__(data=data)
        self._client: Client = client
        self._update(data)

    def __repr__(self) -> str:
        return f'<User puuid={self.puuid!r} game_name={self.game_name!r} tag_line={self.tag_line!r} region={self.region!r}>'

    async def update_identities(self) -> None:
        ...
        # match_history = await self._client.fetch_match_history(puuid=self.puuid, end=1)
        # if match_history is not None:
        #     for match in match_history:
        #         for player in match.players:
        #             if player.puuid == self.puuid:
        #                 self.name = player.name
        #                 self.tag = player.tag
        #                 self.player_card = player.player_card
        #                 self.player_title = player.player_title
        #                 self.level_border = player.level_border
        #                 self.account_level = player.account_level
        #                 self.last_update = match.started_at
        # TODO: return rank
        # data = await self._client.http.get_user_data(self.puuid)
        # self._update(data)
