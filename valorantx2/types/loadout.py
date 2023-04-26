from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class Spray(TypedDict):
    EquipSlotID: str
    SprayID: str
    SprayLevelID: Optional[str]


class Gun(TypedDict):
    ID: str
    SkinID: str
    SkinLevelID: str
    ChromaID: str
    CharmInstanceID: NotRequired[str]
    CharmID: NotRequired[str]
    CharmLevelID: NotRequired[str]
    Attachments: List[Any]


class Identity(TypedDict):
    PlayerCardID: str
    PlayerTitleID: str
    AccountLevel: int
    PreferredLevelBorderID: str
    HideAccountLevel: bool


class Loadout(TypedDict):
    Subject: str
    Version: int
    Guns: List[Gun]
    Sprays: List[Spray]
    Identity: Identity
    Incognito: bool
