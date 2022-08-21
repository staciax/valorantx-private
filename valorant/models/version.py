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

from .. import utils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import datetime
    from ..client import Client
    from ..types.version import Version as VersionPayload

# fmt: off
__all__ = (
    'Version',
)
# fmt: on

class Version:

    def __init__(self, client: Client, data: VersionPayload) -> None:
        self._client = client
        self.manifest_id: str = data['data']['manifestId']
        self.branch: str = data['data']['branch']
        self.version: str = data['data']['version']
        self.build_version: str = data['data']['buildVersion']
        self.engine_version: str = data['data']['engineVersion']
        self.riot_client_version: str = data['data']['riotClientVersion']
        self._build_date_iso: str = data['data']['buildDate']

    def __str__(self) -> str:
        return self.version

    def __repr__(self) -> str:
        attrs = [
            ('manifest_id', self.manifest_id),
            ('branch', self.branch),
            ('version', self.version),
            ('build_version', self.build_version),
            ('engine_version', self.engine_version),
            ('riot_client_version', self.riot_client_version),
            ('build_date_iso', self.build_date),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    @property
    def build_date(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The build date of the version."""
        return utils.parse_iso_datetime(self._build_date_iso)
