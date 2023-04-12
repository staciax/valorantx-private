from __future__ import annotations

from typing import TYPE_CHECKING

from ..valorant_api.models.weapons import (
    Skin as SkinValorantAPI,
    SkinChroma as SkinChromaValorantAPI,
    SkinLevel as SkinLevelValorantAPI,
    Weapon as WeaponValorantAPI,
)

if TYPE_CHECKING:
    from ..valorant_api.cache import CacheState

    # from ..types.store import Offer as StoreOfferPayload
    from ..valorant_api.types.weapons import (
        Skin as ValorantAPISkinPayload,
        SkinChroma as ValorantAPISkinChromaPayload,
        SkinLevel as ValorantAPISkinLevelPayload,
        Weapon as ValorantAPIWeaponPayload,
    )


# class _Cost:

#     def __init__(self) -> None:
#         self._cost: int = 0

#     @property
#     def cost(self) -> int:
#         return self._cost

#     @cost.setter
#     def cost(self, cost: int) -> None:
#         self._cost = cost

#     @property
#     def price(self) -> int:
#         """:class:`int`: alias for :attr:`cost`"""
#         return self._cost

# class Weapon(WeaponValorantAPI, _Cost):
#     pass
#     # def __init__(self, *, state: CacheState, data: ValorantAPIWeaponPayload) -> None:
#     #     super().__init__(state=state, data=data)


# class Skin(SkinValorantAPI, _Cost):
#     pass
#     # def __init__(self, *, state: CacheState, data: ValorantAPISkinPayload, parent: Weapon) -> None:
#     #     super().__init__(state=state, data=data, parent=parent)


# class SkinLevel(SkinLevelValorantAPI, _Cost):
#     pass
#     # def __init__(self, *, state: CacheState, data: ValorantAPISkinLevelPayload, parent: Skin, level_number: int) -> None:
#     #     super().__init__(state=state, data=data, parent=parent, level_number=level_number)


# class SkinChroma(SkinChromaValorantAPI, _Cost):
#     pass
# def __init__(self, *, state: CacheState, data: ValorantAPISkinChromaPayload, parent: Skin) -> None:
#     super().__init__(state=state, data=data, parent=parent)
