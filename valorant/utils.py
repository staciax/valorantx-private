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

import uuid
import json
import datetime

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse


def is_uuid(value: str) -> bool:
    """
    Checks if a string is a valid UUID.
    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def _to_dict(text: str) -> dict:
    """Convert text to dict"""
    return json.loads(text)


async def json_or_text(response: ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding='utf-8')
    if 'Content-Type' in response.headers:
        if response.headers['Content-Type'] == 'application/data':
            return await response.json()

    try:
        return _to_dict(text)
    except (json.JSONDecodeError, TypeError):
        return text


class _MissingSentinel:
    __slots__ = ()

    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __hash__(self):
        return 0

    def __repr__(self):
        return '...'


MISSING: Any = _MissingSentinel()


def iso_to_datetime(iso: str) -> datetime.datetime:
    """Convert ISO8601 string to datetime"""
    try:
        dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ')
    return dt.replace(tzinfo=datetime.timezone.utc)  # or None


def percent(*args: int) -> Optional[List[Union[int, float]]]:
    """Calculate percent of a list of integers"""
    t = sum(args)
    return [100 * y / t for y in args]
