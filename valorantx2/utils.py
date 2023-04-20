from __future__ import annotations

import uuid
from typing import List, Tuple, Union

from .valorant_api.utils import MISSING as MISSING, json_or_text as json_or_text, parse_iso_datetime as parse_iso_datetime

# fmt: off
__all__: Tuple[str, ...] = (
    'calculate_level_xp',
    'is_uuid',
    'percent',
    'json_or_text',
    'MISSING',
    'parse_iso_datetime',
)
# fmt: on


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
