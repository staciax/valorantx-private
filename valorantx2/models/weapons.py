from __future__ import annotations

from typing import TYPE_CHECKING

from ..valorant_api.models.weapons import (
    Skin as ValorantAPISkin,
    SkinChroma as ValorantAPISkinChroma,
    SkinLevel as ValorantAPISkinLevel,
    Weapon as ValorantAPIWeapon,
)

if TYPE_CHECKING:
    from ..types.store import Offer as StoreOfferPayload
    from ..valorant_api.types.weapons import (
        Skin as ValorantAPISkinPayload,
        SkinChroma as ValorantAPISkinChromaPayload,
        SkinLevel as ValorantAPISkinLevelPayload,
        Weapon as ValorantAPIWeaponPayload,
    )


class Weapon(ValorantAPIWeapon):
    ...


class Skin(ValorantAPISkin):
    ...


class SkinLevel(ValorantAPISkinLevel):
    ...


class SkinChroma(ValorantAPISkinChroma):
    ...
