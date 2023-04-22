from aiohttp import ClientSession

from valorantx2.valorant_api.client import Client as ClientValorantAPI
from valorantx2.valorant_api.http import HTTPClient

from .enums import Locale
from .models.store import Offers
from .valorant_api_cache import CacheState


class Client(ClientValorantAPI):
    def __init__(self, session: ClientSession, locale: Locale) -> None:
        super().__init__(session, locale)
        self.http: HTTPClient = HTTPClient(session)
        self._cache: CacheState = CacheState(locale=locale, http=self.http)

    def insert_cost(self, offers: Offers) -> None:
        for offer in offers.offers:
            self._cache.insert_cost(offer.id, offer.cost)
