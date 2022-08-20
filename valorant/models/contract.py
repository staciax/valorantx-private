"""
The MIT License (MIT)

Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import datetime

from .base import BaseModel

from .. import utils
from ..asset import Asset
from ..localization import Localization

from typing import Optional, Dict, Any, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

# fmt: off
__all__ = (
    'Contract',
)
# fmt: on

class Contract(BaseModel):

    def __init__(self, client: Client, data: Optional[Dict[str, Any]], user_contract: Any = None) -> None:
        super().__init__(client=client, data=data, user_contract=user_contract)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Contract name={self.name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Optional[Union[str, Dict[str, str]]] = data['displayName']
        self._display_icon: Optional[str] = data['displayIcon']
        self.ship_it: bool = data['shipIt']
        self.free_reward_schedule_uuid: str = data['freeRewardScheduleUuid']
        self.asset_path: str = data['assetPath']

        # content
        self._content: Dict[Any, Any] = data['content']
        self._relation_type: Optional[str] = self._content['relationType']
        self._relation_uuid: Optional[str] = self._content['relationUuid']
        self._chapters: List[Dict[Any, Any]] = self._content['chapters']
        self._premium_reward_schedule_uuid: Optional[str] = self._content['premiumRewardScheduleUuid']
        self._premium_vp_cost: int = self._content['premiumVPCost']

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
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the contract's icon."""
        return Asset._from_url(self._client, self._display_icon)

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
        return utils.parse_iso_datetime(self._expiration_time_iso) if self._expiration_time_iso else None

    # class MissionMeta(NamedTuple):
    #     NPECompleted: bool
    #     WeeklyCheckpoint: str
    #     WeeklyRefillTime: str
