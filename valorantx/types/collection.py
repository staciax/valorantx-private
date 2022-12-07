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

from typing import TYPE_CHECKING, Any, Dict, List, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class SprayLoadout(TypedDict):
    EquipSlotID: str
    SprayID: str
    SprayLevelID: str


class SkinLoadout(TypedDict, total=False):
    ID: str
    SkinID: str
    SkinLevelID: str
    ChromaID: str
    CharmInstanceID: NotRequired[str]
    CharmID: NotRequired[str]
    CharmLevelID: NotRequired[str]
    Attachments: List[Any]


class IdentityLoadout(TypedDict):
    PlayerCardID: str
    PlayerTitleID: str
    AccountLevel: int
    PreferredLevelBorderID: str
    HideAccountLevel: bool


class Loadout(TypedDict):
    Subject: str
    Version: int
    Guns: List[SkinLoadout]
    Sprays: List[SprayLoadout]
    Identity: IdentityLoadout
    Incognito: bool


class Favorite(TypedDict):
    FavoriteID: str
    ItemID: str


class Favorites(TypedDict):
    Subject: str
    FavoritedContent: Dict[str, Favorite]
