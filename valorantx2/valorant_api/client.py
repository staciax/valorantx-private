from typing import List, Optional

import aiohttp

from ..enums import Locale
from .cache import CacheState
from .http import HTTPClient
from .models import Agent


class Client:
    ASSETS = {}

    def __init__(self, session: aiohttp.ClientSession, locale: Locale = Locale.english) -> None:
        self._http: HTTPClient = HTTPClient(session)
        self._cache: CacheState = CacheState(locale=locale, http=self._http)

    async def init(self) -> None:
        ...

    async def fetch(self, version: str) -> None:
        ...

    async def reload(self, *, force: bool = False) -> None:
        ...

    def clear(self) -> None:
        Client.ASSETS.clear()

    @property
    def agents(self) -> List[Agent]:
        return self._cache.agents

    def get_agent(self, uuid: str) -> Optional[Agent]:
        return self._cache.get_agent(uuid)
