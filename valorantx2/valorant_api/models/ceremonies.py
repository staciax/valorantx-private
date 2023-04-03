from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from ...enums import Locale
from ..localization import Localization
from .abc import BaseModel

if TYPE_CHECKING:
    # from typing_extensions import Self
    from ..cache import CacheState
    from ..types.ceremonies import Caremony as CeremonyPayload

# fmt: off
__all__ = (
    'Ceremony',
)
# fmt: on


class Ceremony(BaseModel):
    def __init__(self, state: CacheState, data: CeremonyPayload) -> None:
        super().__init__(data['uuid'])
        self._state: CacheState = state
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self.asset_path: str = data['assetPath']
        self._display_name_localized: Localization = Localization(self._display_name, locale=self._state.locale)

    def __str__(self) -> str:
        return self.display_name.locale

    def __repr__(self) -> str:
        return f'<Ceremony display_name={self.display_name!r}>'

    def display_name_localized(self, locale: Optional[Union[Locale, str]] = None) -> str:
        return self._display_name_localized.from_locale(locale)

    @property
    def display_name(self) -> Localization:
        """:class: `str` Returns the ceremony's name."""
        return self._display_name_localized

    # @classmethod
    # def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
    #     """Returns the ceremony with the given UUID."""
    #     data = client._assets.get_ceremony(uuid)
    #     return cls(client=client, data=data) if data else None
