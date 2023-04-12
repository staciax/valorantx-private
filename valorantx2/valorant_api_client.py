import asyncio

from aiohttp import ClientSession

from .enums import Locale
from .models.store import Offers
from .utils import MISSING
from .valorant_api.client import Client as ClientValorantAPI
from .valorant_api.http import HTTPClient
from .valorant_api_cache import CacheState


class Client(ClientValorantAPI):
    def __init__(self, session: ClientSession, locale: Locale = Locale.english) -> None:
        self._http: HTTPClient = HTTPClient(session)
        self._cache: CacheState = CacheState(locale=locale, http=self._http)
        self._ready: asyncio.Event = MISSING
        self._closed: bool = False

    def insert_cost(self, offers: Offers) -> None:
        for offer in offers.offers:
            self._cache.insert_cost(offer.id, offer.cost)
