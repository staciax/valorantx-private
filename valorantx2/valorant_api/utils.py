from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse


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
