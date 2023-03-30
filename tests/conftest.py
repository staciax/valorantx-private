import os
from typing import AsyncGenerator

import contextlib
import pytest_asyncio
import pytest
from dotenv import load_dotenv

import valorantx

load_dotenv()

username = os.getenv('VALORANT_USERNAME')
assert username is not None
password = os.getenv('VALORANT_PASSWORD')
assert password is not None

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[valorantx.Client, None]:

    async with valorantx.Client(locale=valorantx.Locale.thai) as v_client:
        
        # authorization is required for some endpoints
        with contextlib.suppress(valorantx.errors.RiotAuthenticationError):
            await v_client.authorize(username, password)
        
        await v_client.fetch_assets(reload=True)  # 'with_price=True' is requires authorization
        # after `client.fetch_assets`, you can comment above line and use below line
        # `client.reload_assets(with_price=True)` # will reload assets without authorization
        # if new version available, please use `await client.fetch_assets(with_price=True)` again

        yield v_client

@pytest_asyncio.fixture(scope='class', autouse=True)
def client_class(request) -> None:
    request.cls.client = valorantx.Client(locale=valorantx.Locale.thai)

    
