from __future__ import annotations

import datetime
import json
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union

try:
    import orjson  # type: ignore
except ImportError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True

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


if HAS_ORJSON:
    _from_json = orjson.loads  # type: ignore
else:
    _from_json = json.loads


# source: https://github.com/Rapptz/discord.py/blob/master/discord/http.py
async def json_or_text(response: ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers['content-type'] == 'application/json':
            return _from_json(text)
    except KeyError:
        pass

    # try to parse it as json anyway
    try:
        return _from_json(text)
    except json.JSONDecodeError:
        pass

    return text


# source: https://github.com/Rapptz/discord.py/blob/master/discord/utils.py
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
    return dt.replace(tzinfo=datetime.timezone.utc)


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


def removeprefix(string: str, prefix: str) -> str:
    """Remove prefix from string"""
    # python 3.8 is not supported .removeprefix()
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string
