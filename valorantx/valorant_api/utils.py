from __future__ import annotations

import datetime
import json
from typing import TYPE_CHECKING, Any, Dict, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse

try:
    import orjson  # type: ignore
except ImportError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True

if HAS_ORJSON:

    def _to_json(obj: Any) -> str:
        return orjson.dumps(obj).decode('utf-8')

    _from_json = orjson.loads  # type: ignore
else:

    def _to_json(obj: Any) -> str:
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)

    _from_json = json.loads


# source: https://github.com/Rapptz/discord.py/blob/master/discord/http.py
async def json_or_text(response: ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding='utf-8')

    try:
        if 'application/json' in response.headers['content-type']:
            return _from_json(text)
    except KeyError:
        pass

    # try to parse it as json anyway
    # some endpoints return plain text but it's actually json
    if isinstance(text, str):
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


def string_escape(string: str) -> str:
    # string = string.encode('raw_unicode_escape').decode('unicode_escape')
    string = string.replace('\r\n', ' ')
    string = string.replace('\t', ' ')
    string = string.replace('\r', ' ')
    string = string.replace('\n', ' ')
    string = string.replace('"', '\\"')
    return string


def parse_iso_datetime(iso: str) -> datetime.datetime:
    """Convert ISO8601 string to datetime"""
    try:
        dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%SZ')
    return dt.replace(tzinfo=datetime.timezone.utc)


def removeprefix(string: str, prefix: str) -> str:
    """Remove prefix from string"""
    # python 3.8 is not supported .removeprefix()
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string
