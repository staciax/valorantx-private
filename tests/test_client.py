import pytest

from valorantx.utils import MISSING

from .conftest import BaseTest


class TestInGameAPI(BaseTest):
    @pytest.mark.asyncio
    async def test_client_init(self) -> None:
        assert self.client is not None
        await self.client._init()

    @pytest.mark.asyncio
    async def test_client(self) -> None:
        assert self.client is not None
        assert self.client.is_ready() is False
        assert self.client.is_authorized() is False
        assert self.client.is_closed() is False

        if self.client.is_authorized():
            assert self.client.http._session is not MISSING
        else:
            assert self.client.http._session is MISSING

        await self.client.close()
        assert self.client.is_closed() is True
        assert self.client.http._session is MISSING

        self.client.clear()
        assert self.client.is_ready() is False
        assert self.client.is_authorized() is False
        assert self.client.is_closed() is False

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        await self.client.close()
