from __future__ import annotations

import datetime

from .base import BaseModel

from .. import utils
from ..localization import Localization

from typing import Optional, Dict, Any, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

class Mission(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f'<Mission name={self.title!r}>'

    def __int__(self) -> int:
        return self.xp

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Optional[Union[str, Dict[str, str]]] = data.get('displayName')
        self._title: Optional[Union[str, Dict[str, str]]] = data.get('title')
        self._type: Optional[str] = data.get('type')
        self._xp_grant: int = data.get('xpGrant')
        self._progress_to_complete: int = data.get('progressToComplete')
        self._activation_date_iso: str = data.get('activationDate')
        self._expiration_date_iso: str = data.get('expirationDate')
        self._tags: Optional[List[str]] = data.get('tags')
        self._objectives: Optional[Dict[str, Any]] = data.get('objectives')
        self._asset_path: str = data.get('assetPath')

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the mission's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the mission's name."""
        return self.name_localizations.american_english

    @property
    def title_localizations(self) -> Localization:
        """:class: `Localization` Returns the mission's titles."""
        return Localization(self._title, locale=self._client.locale)

    @property
    def title(self) -> str:
        """:class: `str` Returns the mission's title."""
        return self.title_localizations.american_english

    @property
    def type(self) -> str:
        """:class: `str` Returns the mission's type."""
        return self._type

    @property
    def xp(self) -> int:
        """:class: `int` Returns the mission's xp grant."""
        return self._xp_grant

    @property
    def progress_to_complete(self) -> int:
        """:class: `int` Returns the mission's progress to complete."""
        return self._progress_to_complete

    @property
    def activation_date(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the mission's activation date."""
        return utils.iso_to_datetime(self._activation_date_iso)

    @property
    def expiration_date(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the mission's expiration date."""
        return utils.iso_to_datetime(self._expiration_date_iso)

    @property
    def tags(self) -> List[str]:
        """:class: `list` Returns the mission's tags."""
        return self._tags

    @property
    def objectives(self) -> Dict[str, Any]:
        """:class: `dict` Returns the mission's objectives."""
        return self._objectives

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the mission's asset path."""
        return self._asset_path
