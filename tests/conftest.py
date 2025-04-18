from __future__ import annotations

import asyncio

# import contextlib
import os
from typing import TYPE_CHECKING, AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from valorant import Client as ValorantAPIClient

import valorantx as valorantx

try:
    import uvloop  # type: ignore
except ImportError:
    pass
else:
    uvloop.install()


load_dotenv()

username = os.getenv('RIOT_USERNAME')
assert username is not None
password = os.getenv('RIOT_PASSWORD')
assert password is not None


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[valorantx.Client, None]:
    async with valorantx.Client(locale=valorantx.Locale.thai) as v_client:
        await v_client.authorize(username, password)
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
        # policy = asyncio.get_event_loop_policy()
        # loop = policy.new_event_loop()
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
        await self.client.wait_until_authorized()
        assert self.client.is_authorized() is True
        assert self.client.is_ready() is True
