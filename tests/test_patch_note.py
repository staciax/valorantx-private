from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from valorantx import Client

from valorantx.ext.scrapers import patchnote

@pytest.mark.asyncio
async def test_in_patch_note_scraper(client: Client) -> None:
    tasks = []
    patch_notes = await client.fetch_patch_notes()
    for pn in patch_notes:
        tasks.append(patchnote.PatchNote.fetch_from_url(client, pn.url))

    results = await asyncio.gather(*tasks)
    for result in results:
        assert isinstance(result, patchnote.PatchNote)
