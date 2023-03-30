from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import valorantx


@pytest.mark.usefixtures('client_class')
@pytest.mark.usefixtures('riot_account')
@pytest.mark.asyncio
class TestInGame:
    if TYPE_CHECKING:
        client: valorantx.Client
        riot_username: str
        riot_password: str

    async def test_init(self) -> None:
        await self.client.init()

    async def test_auth(self) -> None:
        await self.client.authorize(self.riot_username, self.riot_password)

    async def test_store_front(self) -> None:
        sf = await self.client.fetch_store_front()
        assert sf is not None
        assert sf.get_store() is not None
        for skin in sf.get_store():
            assert skin is not None
            assert skin.price is not None
            assert isinstance(skin.price, int)

        assert sf.get_bundles() is not None
        for bundle in sf.get_bundles():
            assert bundle is not None
            assert bundle.price is not None
            assert isinstance(bundle.price, int)

        if nmk := sf.get_nightmarket():
            assert nmk is not None
            assert nmk.get_skins() is not None
            for skin in nmk.get_skins():
                assert skin is not None
                assert skin.price is not None
                assert isinstance(skin.price, int)

    async def test_wallet(self) -> None:
        wallet = await self.client.fetch_wallet()
        assert wallet is not None

    async def test_content(self) -> None:
        content = await self.client.fetch_content()
        assert content is not None

    async def test_match_history(self) -> None:
        history = await self.client.fetch_match_history(queue=valorantx.QueueType.unrated, with_details=True)
        assert history is not None
        assert isinstance(history.get_match_details(), list)
        for match in history.get_match_details():
            assert match is not None

    async def test_patch_notes(self) -> None:
        for locale in valorantx.Locale:
            patch_note = await self.client.fetch_patch_notes(locale=locale)
            assert patch_note is not None

    async def test_collection(self) -> None:
        loadout = await self.client.fetch_collection()
        assert loadout is not None
        assert loadout.get_skins() is not None
        for skin in loadout.get_skins():
            assert skin is not None

        assert loadout.get_sprays() is not None
        for spray in loadout.get_sprays():
            assert spray is not None

        assert loadout.get_player_title() is not None
        assert loadout.get_player_card() is not None

        if loadout.get_level_border() is not None:
            assert isinstance(loadout.get_level_border(), valorantx.LevelBorder)

    async def test_close(self) -> None:
        await self.client.close()
        assert self.client._closed
        assert self.client.http._session.closed

    async def test_clear(self) -> None:
        self.client.clear()
        assert not self.client._ready.is_set()
        assert not self.client._assets.ASSET_CACHE
        assert not self.client._assets.OFFER_CACHE
        assert self.client.http._session is valorantx.utils.MISSING
