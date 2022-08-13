from __future__ import annotations

from .base import BaseObject

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

class Agent(BaseObject):

    def __init__(self, client: Client, data: Optional[Any]) -> None:
        super().__init__(client=client, data=data)
