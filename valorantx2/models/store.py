from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client
    from ..types.store import (
        Entitlements as EntitlementsPayload,
        Offers as OffersPayload,
        StoreFront as StoreFrontPayload,
        Wallet as WalletPayload,
    )

__all__ = (
    'StoreFront',
    'Wallet',
    'Entitlements',
    'Offers',
)


class DailyStore:
    def __init__(self, client: Client, data: StoreFrontPayload):
        self.client = client
        self.data = data
        self._skins = None


class BonusStore:
    ...


class StoreFront:
    def __init__(self, client: Client, data: StoreFrontPayload):
        self.client = client
        self.data = data
        self._skins = None
        self._bundle = None
        self._bundles = None
        self._bonus_store = None


class Wallet:
    def __init__(self, client: Client, data: WalletPayload):
        self.client = client
        self.data = data


class Entitlements:
    def __init__(self, client: Client, data: EntitlementsPayload):
        self.client = client
        self.data = data


class Offers:
    def __init__(self, client: Client, data: OffersPayload):
        self.client = client
        self.data = data
