from typing import Generic, TypedDict, TypeVar

T = TypeVar('T')


class Response(TypedDict, Generic[T]):
    data: T
    status: int
