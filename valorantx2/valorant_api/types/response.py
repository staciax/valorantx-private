from typing import Generic, List, TypedDict, TypeVar

T = TypeVar('T')


class Response(TypedDict, Generic[T]):
    data: List[T]
    status: int
