import abc


class BaseModel(abc.ABC):
    __slots__ = ('_uuid',)

    def __init__(self, uuid: str) -> None:
        self._uuid = uuid

    @property
    def uuid(self) -> str:
        return self._uuid

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} uuid={self.uuid!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.uuid == other.uuid

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.uuid)
