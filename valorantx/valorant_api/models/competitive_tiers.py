from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Union

from .. import utils
from ..asset import Asset
from ..enums import Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..cache import CacheState
    from ..types.competitive_tiers import CompetitiveTier as CompetitiveTierPayload, Tier as TierPayload

# fmt: off
__all__ = (
    'CompetitiveTier',
    'Tier',
)
# fmt: on


class Tier:
    def __init__(self, state: CacheState, data: TierPayload) -> None:
        self._state: CacheState = state
        self.tier: int = data['tier']
        self._name: Union[str, Dict[str, str]] = data['tierName']
        self._division: Optional[str] = data['division']
        self._division_name: Union[str, Dict[str, str]] = data['divisionName']
        self.color: str = data['color']
        self.background_color: str = data['backgroundColor']
        self._small_icon: Optional[str] = data['smallIcon']
        self._large_icon: Optional[str] = data['largeIcon']
        self._rank_triangle_down_icon: Optional[str] = data['rankTriangleDownIcon']
        self._rank_triangle_up_icon: Optional[str] = data['rankTriangleUpIcon']
        self._name_locale: Localization = Localization(self._name, locale=self._state.locale)
        self._division_name_localized: Localization = Localization(self._division_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.name.locale

    def __repr__(self) -> str:
        return f'<Tier tier={self.tier!r} name={self.name!r} division={self.division!r}>'

    def __hash__(self) -> int:
        return hash(self.tier)

    def __eq__(self, other) -> bool:
        return isinstance(other, Tier) and self.tier == other.tier

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        return isinstance(other, Tier) and self.tier < other.tier

    def __le__(self, other: object) -> bool:
        return isinstance(other, Tier) and self.tier <= other.tier

    def __gt__(self, other: object) -> bool:
        return isinstance(other, Tier) and self.tier > other.tier

    def __ge__(self, other: object) -> bool:
        return isinstance(other, Tier) and self.tier >= other.tier

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._name_locale.from_locale(locale)

    def division_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._division_name_localized.from_locale(locale)

    @property
    def name(self) -> Localization:
        """:class: `str` Returns the tier's name."""
        return self._name_locale

    @property
    def display_name(self) -> Localization:
        """:class: `Localization` alias for :attr:`name`"""
        return self.name

    @property
    def division(self) -> Optional[str]:
        """:class: `str` Returns the tier's division."""
        return utils.removeprefix(self._division, 'ECompetitiveDivision::') if self._division else None

    @property
    def division_name(self) -> Localization:
        """:class: `str` Returns the tier's division."""
        return self._division_name_localized

    @property
    def small_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the tier's small icon."""
        if self._small_icon is None:
            return None
        return Asset(self._state, self._small_icon)

    @property
    def large_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the tier's large icon."""
        if self._large_icon is None:
            return None
        return Asset(self._state, self._large_icon)

    @property
    def rank_triangle_down_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the tier's rank triangle down icon."""
        if self._rank_triangle_down_icon is None:
            return None
        return Asset(self._state, self._rank_triangle_down_icon)

    @property
    def rank_triangle_up_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the tier's rank triangle up icon."""
        if self._rank_triangle_up_icon is None:
            return None
        return Asset(self._state, self._rank_triangle_up_icon)


class CompetitiveTier(BaseModel):
    def __init__(self, state: CacheState, data: CompetitiveTierPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self.asset_object_name: str = data['assetObjectName']
        self._tiers: List[Tier] = [Tier(state=self._state, data=tier) for tier in data['tiers']]
        self.asset_path: str = data['assetPath']

    def __str__(self) -> str:
        return self.asset_object_name

    def __repr__(self) -> str:
        return f'<CompetitiveTier asset_object_name={self.asset_object_name!r}>'

    @property
    def tiers(self) -> List[Tier]:
        """:class: `list` Returns the competitive tier's tiers."""
        return self._tiers

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the competitive tier with the given UUID."""
    #     data = client._assets.get_competitive_tier(uuid)
    #     return cls(self._state, data=data) if data else None
