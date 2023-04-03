import asyncio
from typing import List, Optional

import aiohttp

from ..enums import Locale
from ..utils import MISSING
from .cache import CacheState
from .http import HTTPClient
from .models import Agent


class Client:
    def __init__(self, session: aiohttp.ClientSession, locale: Locale = Locale.english) -> None:
        self._http: HTTPClient = HTTPClient(session)
        self._cache: CacheState = CacheState(locale=locale, http=self._http)
        self._ready: asyncio.Event = MISSING
        self._closed: bool = False

    async def init(self) -> None:
        self._ready = asyncio.Event()

        await self._cache.init()

        self._ready.set()

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self._http.close()

    def clear(self) -> None:
        self._closed = False
        self._ready.clear()
        self._ready = MISSING
        self._cache.clear()

    async def wait_until_ready(self) -> None:
        if self._ready is not MISSING:
            await self._ready.wait()
        else:
            raise RuntimeError('Client not initialized yet.')

    @property
    def agents(self) -> List[Agent]:
        return self._cache.agents

    def get_agent(self, uuid: str) -> Optional[Agent]:
        return self._cache.get_agent(uuid)
