# Copyright (c) 2023-present STACiA, 2022-present Giorgio(giorgi-o)
# Licensed under the MIT

from __future__ import annotations

import json
import uuid
from typing import Any, List, Union

from valorant.utils import MISSING as MISSING, parse_iso_datetime as parse_iso_datetime

try:
    import orjson  # type: ignore
except ImportError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True

__all__ = (
    'MISSING',
    'calculate_level_xp',
    'is_uuid',
    'parse_iso_datetime',
    'percent',
)

if HAS_ORJSON:

    def _to_json(obj: Any) -> str:
        return orjson.dumps(obj).decode('utf-8')  # type: ignore

    _from_json = orjson.loads  # type: ignore

else:

    def _to_json(obj: Any) -> str:
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)

    _from_json = json.loads


def is_uuid(value: str) -> bool:
    """
    Checks if a string is a valid UUID.
    """
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


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
