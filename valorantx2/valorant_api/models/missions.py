from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from .. import utils
from ..enums import Locale, MissionType, try_enum
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..cache import CacheState
    from ..types.missions import Mission as MissionPayload, Objective as ObjectivePayload

# fmt: off
__all__ = (
    'Mission',
)
# fmt: on


class Objective(BaseModel):
    def __init__(self, data: ObjectivePayload) -> None:
        super().__init__(data['objectiveUuid'])
        self.value: int = data['value']

    # TODO: add magic methods


class Mission(BaseModel):
    def __init__(self, state: CacheState, data: MissionPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Optional[Union[str, Dict[str, str]]] = data['displayName']
        self._title: Optional[Union[str, Dict[str, str]]] = data['title']
        self._type: Optional[str] = data['type']
        self.xp_grant: int = data['xpGrant']
        self.progress_to_complete: int = data['progressToComplete']
        self._activation_date_iso: str = data['activationDate']
        self._expiration_date_iso: str = data['expirationDate']
        self.tags: Optional[List[str]] = data['tags']
        self.objectives: Optional[List[Objective]] = None
        if data['objectives'] is not None:
            self.objectives = [Objective(obj) for obj in data['objectives']]
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)
        self._title_localized: Localization = Localization(self._title, locale=self._state.locale)

    def __str__(self) -> str:
        return self.title.locale

    def __repr__(self) -> str:
        return f'<Mission title={self.title!r}>'

    def __int__(self) -> int:
        return self.xp_grant

    @property
    def xp(self) -> int:
        """:class: `int` alias for :attr: `Mission.xp_grant`"""
        return self.xp_grant

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    def title_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._title_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the mission's name."""
        return self._display_name_localized

    @property
    def title(self) -> Localization:
        """:class: `str` Returns the mission's title."""
        return self._title_localized

    @property
    def type(self) -> Optional[MissionType]:
        """Optional[:class: `MissionType`] Returns the mission's type."""
        if self._type == '' or self._type is None:
            return None
        return try_enum(MissionType, utils.removeprefix(self._type, 'EAresMissionType::'))

    @property
    def activation_date(self) -> Optional[datetime.datetime]:
        """:class: `datetime.datetime` Returns the mission's activation date."""
        return utils.parse_iso_datetime(self._activation_date_iso) if self._activation_date_iso else None

    @property
    def expiration_date(self) -> Optional[datetime.datetime]:
        """:class: `datetime.datetime` Returns the mission's expiration date."""
        return utils.parse_iso_datetime(self._expiration_date_iso) if self._expiration_date_iso else None

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the mission with the given UUID."""
    #     data = client._assets.get_mission(uuid)
    #     return cls(client=client, data=data) if data else None
