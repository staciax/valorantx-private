from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from ..enums import Region, Shard, try_enum

if TYPE_CHECKING:
    from ..types.config import Config as ConfigPayload


class Config:
    def __init__(self, data: ConfigPayload) -> None:
        self.last_application: str = data['LastApplication']
        self.collapsed: Dict[str, str] = data['Collapsed']

    def __repr__(self) -> str:
        return '<Config>'

    @property
    def region(self) -> Region:
        return try_enum(Region, self.collapsed.get('loginqueue.region'))

    @property
    def shard(self) -> Shard:
        return try_enum(Shard, self.collapsed.get('playerfeedbacktool.shard'))
