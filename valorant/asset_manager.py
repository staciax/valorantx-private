from __future__ import annotations

import os
import io
import yarl
from typing import Optional, Union, Any, Tuple, TYPE_CHECKING

from . import utils
from .file import File

MISSING = utils.MISSING

if TYPE_CHECKING:
    from typing_extensions import Self
    from .client import Client

class AssetMixin:

    url: str
    _client: Client

    def read(self):
        if self._client is None:
            raise ValueError('Asset has no client')

        return self._client.http.get_from_url(self.url)

    def save(self, fp: Union[str, bytes, os.PathLike[Any], io.BufferedIOBase], *, seek_begin: bool = True) -> int:
        data = self.read()
        if isinstance(fp, io.BufferedIOBase):
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written
        else:
            with open(fp, 'wb') as f:
                return f.write(data)

    def to_file(self, *, filename: Optional[str] = MISSING) -> File:
        data = self.read()
        file_filename = filename if filename is not MISSING else yarl.URL(self.url).name
        return File(io.BytesIO(data), filename=file_filename)

class Asset(AssetMixin):

    __slot__: Tuple[str, ...] = (
        '_client',
        '_url',
        '_video',
        '_animated'
    )

    def __init__(self, client: Client, url: str, *, animated: bool = False, video: bool = False) -> None:
        self._client = client
        self._url = url
        self._video = video
        self._animated = animated

    @classmethod
    def _from_url(cls, client: Client, url: str, *, animated: bool = False) -> Self:
        video = True if url.endswith('.mp4') else False
        if not animated and url.endswith('.gif'):
            animated = True
        return cls(client=client, url=url, animated=animated, video=video)

    def __str__(self) -> str:
        return str(self._url)

    def __len__(self) -> int:
        return len(self._url)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Asset) and self._url == other._url

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self._url)

    @property
    def url(self) -> str:
        """:class:`str`: Returns the underlying URL of the asset."""
        return self._url

    @property
    def animated(self) -> bool:
        """:class:`bool`: Returns whether the asset is animated."""
        return self._animated

    @property
    def video(self) -> bool:
        """ :class:`bool`: Returns whether the asset is a video."""
        return self._video

