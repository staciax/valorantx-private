from __future__ import annotations

from typing import Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

class _ModelTag:
    __slots__ = ()
    uuid: str

class BaseModel(_ModelTag):
    __slots__ = (
        '_uuid',
        '_client',
        '_extras',
    )

    if TYPE_CHECKING:
        uuid: str
        _client: Client

    def __init__(self, client: Client, data: Union[Any, Any], **kwargs: Any) -> None:
        self._client = client
        self._extras = kwargs
        self._update(data)

    def __str__(self) -> str:
        return self.uuid

    def __repr__(self) -> str:
        return (
            f"<BaseObject uuid={self.uuid}>"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _ModelTag) and other.uuid == self.uuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.uuid)

    def _update(self, data: Union[Any, Any]) -> None:
        self._uuid: str = data.get('uuid', None)

    @property
    def uuid(self) -> str:
        """:class:`str`: The uuid of the object."""
        return self._uuid
