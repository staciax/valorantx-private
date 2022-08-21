"""
The MIT License (MIT)

Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import datetime

from .base import BaseModel

from .. import utils
from ..enums import Locale
from ..asset import Asset

from typing import Any, List, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client

__all__ = (
    'PatchNotes',
    'PatchNote'
)

class PatchNotes:

    def __init__(self, *, client: Client, data: Any, locale: Union[str, Locale]) -> None:
        self._client: Client = client
        self.locale: Union[str, Locale] = locale
        self.component_chunk_name: str = data['componentChunkName']
        self.path: str = data['path']
        self._result: Dict[str, Any] = data['result']
        self._result_data: Dict[str, Any] = self._result['data']
        self._articles: List[Dict[str, Any]] = self._result_data['articles']['nodes']
        self._page_context: Dict[str, Any] = self._result['pageContext']
        self._static_query_hashes: List[str] = data['staticQueryHashes']

    def __repr__(self) -> str:
        return f'<PatchNotes title={self.title!r} patch_notes={self.patch_notes!r}>'

    @property
    def see_article_title(self) -> str:
        return self.page_context['localization']['news']['seeArticle']

    @property
    def title(self) -> str:
        return self._result_data['tag']['title']

    @property
    def _config(self) -> List[Dict[str, Any]]:
        return self._result_data['config']['nodes']

    @property
    def page_context(self) -> Dict[str, Any]:
        return self._page_context

    @property
    def patch_notes(self) -> List[PatchNote]:
        return [PatchNote(
            client=self._client,
            data=article,
            locale=self.locale
        ) for article in self._articles]

    @property
    def last_patch_note(self) -> PatchNote:
        return PatchNote(client=self._client, data=self._articles[0], locale=self.locale)

class PatchNote:

    BASE_URL = 'https://playvalorant.com'

    def __init__(self, *, client: Client, data: Any, locale: Union[str, Locale]) -> None:
        self._client = client
        self.locale: str = str(locale)
        self._update(data)

    def __repr__(self) -> str:
        return f'<PatchNote title={self.title!r}>'

    def __hash__(self) -> int:
        return hash(self.id)

    def _update(self, data: Any) -> None:
        self.id: str = data['id']
        self.uid: str = data['uid']
        self.title: str = data['title']
        self.description: str = data['description']
        self.url: str = self.BASE_URL + '/' + self.locale.lower() + data['url']['url']
        self.external_link: Optional[str] = data['external_link']
        self._banner = data['banner']
        self._banner_url: str = self._banner['url']
        self._banner_height: int = self._banner['dimension']['height']
        self._banner_width: int = self._banner['dimension']['width']
        self._banner_content_type: str = self._banner['content_type']
        self._banner_file_size: str = self._banner['file_size']
        self._banner_filename: str = self._banner['filename']
        self.article_type: str = data['article_type']
        self._date_iso: str = data['date']
        self._category_title: str = data['category']

    @property
    def banner(self) -> Asset:
        return Asset._from_url(client=self._client, url=self._banner_url)

    @property
    def timestamp(self) -> datetime.datetime:
        return utils.parse_iso_datetime(self._date_iso)

    @property
    def category_title(self) -> Optional[str]:
        if len(self._category_title) > 0:
            return self._category_title[0]
