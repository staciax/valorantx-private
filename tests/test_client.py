import pytest

from valorantx2.utils import MISSING

from .conftest import BaseAuthTest


class TestInGameAPI(BaseAuthTest):
    @pytest.mark.asyncio
    async def test_client_init(self) -> None:
        await self.client.init()

    @pytest.mark.asyncio
    async def test_client(self) -> None:
        assert self.client is not None

        assert self.client.is_ready() is True
        assert self.client.is_authorized() is True
        assert self.client.is_closed() is False
        assert self.client._http._session is not MISSING

        await self.client.close()
        assert self.client.is_closed() is True
        assert self.client._http._session is not MISSING

        self.client.clear()
        assert self.client.is_ready() is False
        assert self.client.is_authorized() is False
        assert self.client.is_closed() is False
