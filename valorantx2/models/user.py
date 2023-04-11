from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..types.user import PartialUser as PartialUserPayload

__all__ = ('ClientUser',)


class _BaseUser:
    puuid: str
    __slots__ = ()


class ClientUser(_BaseUser):
    _username: Optional[str]
    _tagline: Optional[str]
    _region: Optional[str]

    def __init__(self, *, data: PartialUserPayload) -> None:
        self._puuid: str = data["puuid"]
        self._update(data)

    def __str__(self) -> str:
        return f'{self.username}#{self.tagline}'

    def __repr__(self) -> str:
        return (
            f"<ClientUser puuid={self.puuid!r} username={self.username!r} tagline={self.tagline!r} region={self.region!r}>"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ClientUser) and other.puuid == self.puuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.puuid)

    def _update(self, data: PartialUserPayload) -> None:
        self._username = data["name"]
        self._tagline = data["tag"]
        self._region = data["region"]

    @property
    def puuid(self) -> str:
        return self._puuid

    @property
    def username(self) -> str:
        return self._username or ''

    @property
    def tagline(self) -> str:
        return self._tagline or ''

    @property
    def region(self) -> str:
        return self._region or ''

    @property
    def display_name(self) -> str:
        return f"{self.username}#{self.tagline}"
