from __future__ import annotations

from typing import TYPE_CHECKING

from ..valorant_api.models.weapons import (
    Skin as SkinValorantAPI,
    SkinChroma as SkinChromaValorantAPI,
    SkinLevel as SkinLevelValorantAPI,
    Weapon as WeaponValorantAPI,
)
from .abc import _Cost

if TYPE_CHECKING:
    from ..valorant_api.types.weapons import (
        Skin as ValorantAPISkinPayload,
        SkinChroma as ValorantAPISkinChromaPayload,
        SkinLevel as ValorantAPISkinLevelPayload,
        Weapon as ValorantAPIWeaponPayload,
    )
    from ..valorant_api_cache import CacheState


class Weapon(WeaponValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: ValorantAPIWeaponPayload) -> None:
        super().__init__(state=state, data=data)


class Skin(SkinValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinPayload, parent: Weapon) -> None:
        super().__init__(state=state, data=data, parent=parent)


class SkinLevel(SkinLevelValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinLevelPayload, parent: Skin, level_number: int) -> None:
        super().__init__(state=state, data=data, parent=parent, level_number=level_number)


class SkinChroma(SkinChromaValorantAPI, _Cost):
    def __init__(self, *, state: CacheState, data: ValorantAPISkinChromaPayload, parent: Skin) -> None:
        super().__init__(state=state, data=data, parent=parent)
