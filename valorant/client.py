from __future__ import annotations

import os
import json
import asyncio
import logging
from .enums import Locale

from .http import HTTPClient
from .asset import Asset
from typing import Any, Coroutine, Generator, Mapping, Optional, Type, Union, TYPE_CHECKING

__all__ = ("Client",)

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing_extensions import Self
    from types import TracebackType

class Client:

    def __init__(self, *, locale: Union[Locale, str] = Locale.american_english) -> None:

        # http client
        self.http: HTTPClient = HTTPClient()

        # asset
        self.asset: Asset = Asset(client=self, locale=locale)

        # locale
        self._locale: str = str(locale)

        # config
        self._closed: bool = False
        self._ready: bool = False
        self._version: Optional[str] = None

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

    # asset

    async def fetch_all_assets(self) -> None:
        await self.asset.fetch_all_assets()



