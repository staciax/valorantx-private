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

import os
import json
import asyncio
import logging

from .enums import Locale, QueueID
from .http import HTTPClient
from .assets import Assets

from .models import (
    GameContent,
    MMR,
    Wallet
)

from typing import (
    Any,
    Coroutine,
    Generator,
    Mapping,
    Optional,
    Type,
    Union,
    TYPE_CHECKING,
)

__all__ = ('Client',)

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing_extensions import Self
    from types import TracebackType

class Client:

    def __init__(self, *, locale: Union[Locale, str] = Locale.american_english) -> None:

        # http client
        self.http: HTTPClient = HTTPClient()

        # config
        self._closed: bool = False
        self._ready: bool = False
        self._version: Optional[str] = None
        self._season: Optional[str] = None

        # locale
        self._locale: str = locale

        # assets
        self.assets: Assets = Assets(client=self, locale=locale)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if not self.is_closed():
            await self.close()

    def activate(self) -> None:
        ...
        # self.version = self.http.get_valorant_version()
        # self.season = self.http.get_valorant_season()
        #  TODO: fetch version and season

    async def close(self) -> None:

        if self._closed:
            return
        self._closed = True
        await self.http.close()

    def is_closed(self) -> bool:
        return self._closed

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def version(self) -> Optional[str]:
        return self._version

    @version.setter
    def version(self, value: Optional[str]) -> None:
        self._version = value

    @locale.setter
    def locale(self, locale: str) -> None:
        self._locale = locale

    # PVP endpoints

    def fetch_game_content(self) -> GameContent:
        return GameContent(client=self, data=self.http.fetch_content())

    def fetch_account_xp(self) -> Coroutine[Any, Any, None]:
        return self.http.fetch_account_xp()

    # async def fetch_player_loadout(self) -> Collection:
    #     account_xp = await self.http.fetch_account_xp()
    #     self.user._account_level = account_xp['Progress']['Level']
    #     data = await self.http.fetch_player_loadout()
    #     return Collection(client=self, data=data)

    def put_player_loadout(self, loadout: Mapping) -> Coroutine[Any, Any, None]:
        return self.http.put_player_loadout(loadout)

    def fetch_player_mmr(self, puuid: Optional[str] = None) -> MMR:
        data = await self.http.fetch_mmr(puuid)
        return MMR(client=self, data=data)

    # async def fetch_player_match_history(
    #     self,
    #     puuid: Optional[str] = None,
    #     start_index: int = 0,
    #     end_index: int = 15,
    #     queue_id: Optional[str, QueueID] = QueueID.unrated,
    # ) -> FetchMatchHistory:
    #     data = await self.http.fetch_match_history(puuid, start_index, end_index, queue_id)
    #     return FetchMatchHistory(client=self, data=data)

    # async def fetch_match_details(self, match_id: str) -> Any:
    #     match_details = await self.http.fetch_match_details(match_id)
    #     return MatchDetail(client=self, data=match_details)

    # # store endpoints
    #
    # async def fetch_storefront(self) -> StoreFront:
    #     data = await self.http.store_fetch_storefront()
    #     return StoreFront(client=self, data=data)

    async def fetch_wallet(self) -> Wallet:
        data = await self.http.store_fetch_wallet()
        return Wallet(client=self, data=data)

    # async def fetch_patch_notes(self, locale: str) -> PatchNotes:
    #     data = await self.http.fetch_patch_notes(locale)
    #     return PatchNotes(client=self, data=data, locale=locale)

    # asset

    async def fetch_all_assets(self, force: bool = False) -> None:
        await self.assets.fetch_all_assets(force=force)
