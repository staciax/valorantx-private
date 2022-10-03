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
import json
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union

from .. import utils
from ..asset import Asset
from ..enums import Locale

if TYPE_CHECKING:
    from ..client import Client


__all__ = ('PatchNotes', 'PatchNote')


class PageData:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.locales: Dict[str, Any] = data['locales']
        self.locale_edges: List[Dict[str, Any]] = self.locales['edges']
        self.title: str = data['tag']['title']
        self.articles: Dict[str, Any] = data['articles']
        self.article_nodes: List[Dict[str, Any]] = self.articles['nodes']
        self.config: Dict[str, Any] = data['config']
        self.config_nodes: List[Dict[str, Any]] = self.config['nodes']

    def __repr__(self) -> str:
        return f'<PageData title={self.title!r}>'


class Result:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.page_data: PageData = PageData(data['data'])
        self.page_context: PageContext = PageContext(data=data['pageContext'])

    def __repr__(self) -> str:
        return f'<Result page_context={self.page_context!r}>'


class PageContext:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.uid: str = data['uid']
        self.environment: str = data['environment']
        self.locale: str = data['locale']
        self.language: str = data['language']
        self.original_path: str = 'https://playvalorant.com' + data['originalPath']
        self.bcp47locale: str = data['bcp47locale']
        self.localized_routes: Dict[str, str] = data['localizedRoutes']
        self.i18n: Dict[str, Any] = data['i18n']

    def __repr__(self) -> str:
        return f'<PageContext locale={self.locale!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PageContext) and self.uid == other.uid and self.locale == other.locale

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class PatchNotes:
    def __init__(self, *, client: Client, data: Any, locale: Union[str, Locale]) -> None:
        self._client: Client = client
        self.locale: Union[str, Locale] = locale
        self.component_chunk_name: str = data['componentChunkName']
        self.path: str = data['path']
        self.result: Result = Result(data=data['result'])
        self._static_query_hashes: List[str] = data['staticQueryHashes']

    def __repr__(self) -> str:
        return f'<PatchNotes title={self.title!r} patch_notes={self.patch_notes!r}>'

    def __iter__(self) -> Iterator[PatchNote]:
        for node in self.result.page_data.article_nodes:
            yield PatchNote(client=self._client, data=node, locale=self.locale)

    def __len__(self) -> int:
        return len(self.patch_notes)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PatchNotes)
            and self._static_query_hashes == other._static_query_hashes
            and self.locale == other.locale
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def see_article_title(self) -> str:
        try:
            for edge in self.result.page_data.locale_edges:
                if edge['node']['ns'] == 'home':
                    data = edge['node']['data']
                    to_dict = json.loads(data)
                    return to_dict.get('news.seeArticle', 'See Article')
        except (KeyError, TypeError):
            return 'See Article'

    @property
    def title(self) -> str:
        return self.result.page_data.title

    @property
    def patch_notes(self) -> List[PatchNote]:
        return [
            PatchNote(client=self._client, data=node, locale=self.locale) for node in self.result.page_data.article_nodes
        ]

    @property
    def latest(self) -> Optional[PatchNote]:
        if len(self.result.page_data.article_nodes) > 0:
            return PatchNote(client=self._client, data=self.result.page_data.article_nodes[0], locale=self.locale)
        return None


class PatchNote:

    BASE_URL = 'https://playvalorant.com'

    def __init__(self, *, client: Client, data: Any, locale: Union[str, Locale]) -> None:
        self._client = client
        self.locale: str = str(locale)
        self.id: str = data['id']
        self.uid: str = data['uid']
        self.title: str = data['title']
        self.description: str = data['description']
        self._url: str = self.BASE_URL + '/' + self.locale.lower() + data['url']['url']
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
        self._category_title: List[Dict[str, str]] = data['category']

    def __repr__(self) -> str:
        return f'<PatchNote title={self.title!r} locale={self.locale!r}>'

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PatchNote) and self.id == other.id and self.locale == other.locale

    @property
    def url(self) -> str:
        return self._url

    @property
    def version(self) -> float:
        digits = [i for i in self.title if i.isdigit()]
        try:
            version = float(digits[0] + '.' + ''.join(digits[1:]))
        except (IndexError, ValueError):
            return 0.0
        else:
            return version

    @property
    def banner(self) -> Asset:
        return Asset._from_url(client=self._client, url=self._banner_url)

    @property
    def timestamp(self) -> datetime.datetime:
        return utils.parse_iso_datetime(self._date_iso)

    @property
    def category_title(self) -> Optional[str]:
        if len(self._category_title) > 0:
            return self._category_title[0]['title']
