from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types.name_service import NameServive as NameServicePayload

# fmt: off
__all__ = (
    'NameService',
)
# fmt: on


class NameService:
    def __init__(self, data: NameServicePayload) -> None:
        self.display_name: str = data['DisplayName']
        self.subject: str = data['Subject']
        self.game_name: str = data['GameName']
        self.tag_line: str = data['TagLine']

    def __repr__(self) -> str:
        return f'<NameService subject={self.subject} game_name={self.game_name} tag_line={self.tag_line}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NameService) and other.subject == self.subject

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.subject)
