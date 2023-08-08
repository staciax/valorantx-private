from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from valorant.asset import Asset as _Asset

# fmt: off
__all__ = (
    'Asset',
)
# fmt: on

if TYPE_CHECKING:
    from typing_extensions import Self

    from .client import Client


class Asset(_Asset):
    _state: Client

    if TYPE_CHECKING:

        def __init__(self, state: Client, url: str, *, animated: bool = False, video: bool = False) -> None:
            ...

        @classmethod
        def _from_url(cls, state: Client, url: Optional[str] = None, *, animated: bool = False) -> Self:
            ...
