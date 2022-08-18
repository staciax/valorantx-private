from __future__ import annotations

from ..localization import Localization
from .base import BaseModel

from typing import Any, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

# fmt: off
__all__ = (
    'Agent',
)
# fmt: on

# https://dash.valorant-api.com/endpoints/agents

class Agent(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __repr__(self) -> str:
        return f'<Agent name={self.name!r}>'

    def __str__(self) -> str:
        return self.name

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the agent's name."""
        return self.name_localizations.american_english
