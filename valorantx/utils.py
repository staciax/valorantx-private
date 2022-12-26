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
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse

__all__: Tuple[str, ...] = (
    'is_uuid',
    'json_or_text',
    'MISSING',
    'parse_iso_datetime',
    'percent',
)


def is_uuid(value: str) -> bool:
    """
    Checks if a string is a valid UUID.
    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def _unescape(string: str) -> str:
    string = string.replace(r"\\", "\\")
    string = string.replace(r"\t", "\t")
    string = string.replace(r"\r", "\r")
    string = string.replace(r"\n", "\n")
    string = string.replace(r"\"", '"')
    return string


def string_escape(string: str) -> str:
    # string = string.encode('raw_unicode_escape').decode('unicode_escape')
    string = string.replace('\r\n', ' ')
    string = string.replace('\t', ' ')
    string = string.replace('\r', ' ')
    string = string.replace('\n', ' ')
    string = string.replace('"', '\\"')
    return string


def _to_dict(text: str) -> Dict[Any, Any]:
    """Convert text to dict"""
    return json.loads(text)

# source: https://github.com/Rapptz/discord.py/blob/master/discord/http.py
async def json_or_text(response: ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers['content-type'] == 'application/json':
            return _to_dict(text)
    except KeyError:
        pass

    # try to parse it as json anyway
    try:
        return _to_dict(text)
    except json.JSONDecodeError:
        pass
    
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


def parse_iso_datetime(iso: str) -> datetime.datetime:
    """Convert ISO8601 string to datetime"""
    try:
        dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ')
    return dt.replace(tzinfo=datetime.timezone.utc)  # or None


def percent(*args: int) -> List[Union[int, float]]:
    """Calculate percent of a list of integers"""
    t = sum(args)
    return [100 * y / t for y in args]


# -- source idea by https://github.com/giorgi-o


def calculate_level_xp(level: int) -> int:
    """Returns the xp required for the given level."""
    level_multiplier = 750
    if 2 <= level <= 50:
        return 2000 + (level - 2) * level_multiplier
    elif 51 <= level <= 55:
        return 36500
    else:
        return 0


# --
