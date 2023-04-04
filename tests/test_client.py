import pytest

from valorantx2.utils import MISSING

from .conftest import BaseTest


class TestInGameAPI(BaseTest):
    @pytest.mark.asyncio
    async def test_client_init(self) -> None:
        await self.client.init()

    @pytest.mark.asyncio
    async def test_client(self) -> None:
        assert self.client is not None

        assert self.client.is_ready() is False
        assert self.client.is_authorized() is False
        assert self.client.is_closed() is False

        if self.client.is_authorized():
            assert self.client._http._session is not MISSING
        else:
            assert self.client._http._session is MISSING

        await self.client.close()
        assert self.client.is_closed() is True
        assert self.client._http._session is MISSING

        self.client.clear()
        assert self.client.is_ready() is False
        assert self.client.is_authorized() is False
        assert self.client.is_closed() is False
