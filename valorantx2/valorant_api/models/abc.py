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
