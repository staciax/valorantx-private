from __future__ import annotations

import asyncio

# import contextlib
import os
from typing import TYPE_CHECKING, AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv

import valorantx2 as valorantx
from valorantx2.valorant_api import Client as ValorantAPIClient

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()


load_dotenv()

username = os.getenv('VALORANT_USERNAME')
assert username is not None
password = os.getenv('VALORANT_PASSWORD')
assert password is not None


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[valorantx.Client, None]:
    async with valorantx.Client(locale=valorantx.Locale.thai) as v_client:
        # await v_client.fetch_assets(reload=True, force=True)  # 'with_price=True' is requires authorization
        # after `client.fetch_assets`, you can comment above line and use below line
        # `client.reload_assets(with_price=True)` # will reload assets without authorization
        # if new version available, please use `await client.fetch_assets(with_price=True)` again

        yield v_client


@pytest_asyncio.fixture(scope='class')
def client_class(request) -> None:
    client = valorantx.Client(locale=valorantx.Locale.thai)
    request.cls.client = client
    request.cls.valorant_api = client.valorant_api


@pytest.fixture(scope='class')
def riot_account(request) -> None:
    request.cls.riot_username = username
    request.cls.riot_password = password


@pytest.fixture(scope='session')
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.usefixtures('client_class')
@pytest.mark.usefixtures('riot_account')
class BaseTest:
    if TYPE_CHECKING:
        client: valorantx.Client
        riot_username: str
        riot_password: str
        valorant_api: ValorantAPIClient

    def test_client(self) -> None:
        assert self.client is not None
        assert self.client.is_authorized() is False
        assert self.client.is_ready() is False


class BaseAuthTest(BaseTest):
    @pytest.mark.asyncio
    async def test_authorize(self) -> None:
        assert self.client is not None
        assert self.client.is_ready() is False
        await self.client.authorize(self.riot_username, self.riot_password)
        await self.client.wait_until_ready()
        assert self.client.is_authorized() is True
        assert self.client.is_ready() is True
