import pytest

from .conftest import BaseAuthTest


class TestInGameAPI(BaseAuthTest):
    @pytest.mark.asyncio
    async def test_close(self):
        await self.client.close()
