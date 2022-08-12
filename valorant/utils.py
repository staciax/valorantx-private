from __future__ import annotations

import uuid
import json
import datetime

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse

def validate_uuid(value: str) -> bool:
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
    """ Convert ISO8601 string to datetime """
    dt = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%fZ')
    return dt.replace(tzinfo=datetime.timezone.utc)  # or None


def percent(*args: int) -> Optional[List[Union[int, float]]]:
    """ Calculate percent of a list of integers """
    t = sum(args)
    return [100 * y / t for y in args]
