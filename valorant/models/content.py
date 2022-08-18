from __future__ import annotations

from .base import BaseModel

from ..asset import Asset
from ..localization import Localization

from ..utils import iso_to_datetime

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import datetime
    from ..client import Client

__all__ = (
    'Mission',
    'ContentTier',
    'Contract'
)

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
        return iso_to_datetime(self._activation_date_iso)

    @property
    def expiration_date(self) -> datetime.datetime:
        """:class: `datetime.datetime` Returns the mission's expiration date."""
        return iso_to_datetime(self._expiration_date_iso)

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

class ContentTier(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<ContentTier name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Optional[Union[str, Dict[str, str]]] = data.get('displayName')
        self._dev_name: str = data.get('devName')
        self._rank: int = data.get('rank')
        self._juice_value: int = data.get('juiceValue')
        self._juice_cost: int = data.get('juiceCost')
        self._highlight_color: str = data.get('highlightColor')
        self._display_icon: str = data.get('displayIcon')
        self._asset_path: str = data.get('assetPath')

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the content tier's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the content tier's name."""
        return self.name_localizations.american_english

    @property
    def dev_name(self) -> str:
        """:class: `str` Returns the content tier's dev name."""
        return self._dev_name

    @property
    def rank(self) -> int:
        """:class: `int` Returns the content tier's rank."""
        return self._rank

    @property
    def juice_value(self) -> int:
        """:class: `int` Returns the content tier's juice value."""
        return self._juice_value

    @property
    def juice_cost(self) -> int:
        """:class: `int` Returns the content tier's juice cost."""
        return self._juice_cost

    @property
    def highlight_color(self) -> str:
        """:class: `str` Returns the content tier's highlight color RGBA."""
        return self._highlight_color

    @property
    def icon(self) -> Asset:
        """:class: `Asset` Returns the content tier's icon."""
        return Asset._from_url(self._client, self._display_icon)

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the content tier's asset path."""
        return self._asset_path

class Contract(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]], user_contract: Any = None) -> None:
        super().__init__(client=client, data=data, user_contract=user_contract)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Contract name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Optional[Union[str, Dict[str, str]]] = data.get('displayName')
        self._display_icon: Optional[str] = data.get('displayIcon')
        self._ship_it: bool = data.get('shipIt')
        self._free_reward_schedule_uuid: str = data.get('freeRewardScheduleUuid')

        # content
        self._content: Dict[Any, Any] = data.get('content')
        self._relation_type: Optional[str] = self._content.get('relationType')
        self._relation_uuid: Optional[str] = self._content.get('relationUuid')
        self._chapters: List[Dict[Any, Any]] = self._content.get('chapters')
        self._premium_reward_schedule_uuid: Optional[str] = self._content.get('premiumRewardScheduleUuid')
        self._premium_vp_cost: int = self._content.get('premiumVPCost')

        self._asset_path: str = data.get('assetPath')

        self._complete: bool = False
        self._objectives: Dict[str, Any] = {}
        self._expiration_time: Optional[datetime.datetime] = None

        if self._extras.get('user_contract'):
            self._user_contract: Dict[Any, Any] = self._extras.get('user_contract')
            self._complete = self._user_contract.get('complete')
            self._objectives = self._user_contract.get('contract_objectives')
            self._expiration_time_iso = self._user_contract.get('expiration_time')

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the contract's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def name(self) -> str:
        """:class: `str` Returns the contract's name."""
        return self.name_localizations.american_english

    @property
    def icon(self) -> Asset:
        """:class: `Asset` Returns the contract's icon."""
        return Asset._from_url(self._client, self._display_icon)

    @property
    def ship_it(self) -> bool:
        """:class: `bool` Returns whether the contract is ship it."""
        return self._ship_it

    @property
    def free_reward_schedule_uuid(self) -> str:
        """:class: `str` Returns the contract's free reward schedule uuid."""
        return self._free_reward_schedule_uuid

    @property
    def relation_type(self) -> Optional[str]:
        """:class: `str` Returns the contract's relation type."""
        return self._relation_type

    @property
    def relation_uuid(self) -> Optional[str]:
        """:class: `str` Returns the contract's relation uuid."""
        return self._relation_uuid

    @property
    def chapters(self) -> List[Dict[Any, Any]]:  # https://dash.valorant-api.com/endpoints/contracts
        """:class: `list` Returns the contract's chapters."""
        return self._chapters

    @property
    def premium_reward_schedule_uuid(self) -> Optional[str]:
        """:class: `str` Returns the contract's premium reward schedule uuid."""
        return self._premium_reward_schedule_uuid

    @property
    def premium_vp_cost(self) -> int:
        """:class: `int` Returns the contract's premium vp cost."""
        return self._premium_vp_cost

    @property
    def asset_path(self) -> str:
        """:class: `str` Returns the contract's asset path."""
        return self._asset_path

    # user contract

    @property
    def complete(self) -> bool:
        """:class: `bool` Returns whether the contract is complete."""
        return self._complete

    @property
    def objectives(self) -> Dict[str, Any]:
        """:class: `dict` Returns the contract's objectives."""
        return self._objectives

    @property
    def expiration_time(self) -> Optional[datetime.datetime]:
        """:class: `datetime.datetime` Returns the contract's expiration time."""
        return iso_to_datetime(self._expiration_time_iso) if self._expiration_time_iso else None

    # class MissionMeta(NamedTuple):
    #     NPECompleted: bool
    #     WeeklyCheckpoint: str
    #     WeeklyRefillTime: str
