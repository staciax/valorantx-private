from __future__ import annotations

from ..localization import Localization
from .base import BaseObject

from typing import Any, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

__all__ = ('Agent',)

# https://dash.valorant-api.com/endpoints/agents

class Agent(BaseObject):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def _update(self, data: Optional[Any]) -> None:
        self._display_name: Union[str, Dict[str, str]] = data['displayName']

    def __repr__(self) -> str:
        return f'<Agent uuid={self.uuid!r} name={self.name!r}>'

    def __str__(self) -> str:
        return self.name

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the agent's name."""
        return self.name_localizations.american_english
