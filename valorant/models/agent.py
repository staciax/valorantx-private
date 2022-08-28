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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ..asset import Asset
from ..enums import Locale
from ..localization import Localization
from .base import BaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..client import Client

# fmt: off
__all__ = (
    'Agent',
)
# fmt: on

# https://dash.valorant-api.com/endpoints/agents

# TODO: _agent abilities, voice lines, mediaList, etc.


class AgentRole:
    def __init__(self, client: Client, data: Dict[str, Any]) -> None:
        self._client = client
        self.uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']

    def __repr__(self) -> str:
        return f'<AgentRole display_name={self.display_name!r}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent role's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the agent role's name."""
        return self.name_localizations.american_english

    @property
    def description_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent role's descriptions."""
        return Localization(self._description, locale=self._client.locale)

    @property
    def description(self) -> str:
        """:class: `str` Returns the agent role's description."""
        return self.description_localizations.american_english

    @property
    def display_icon(self) -> Optional[Asset]:
        """:class: `Asset` Returns the agent role's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)


class AgentAbility:
    def __init__(self, client: Client, data: Dict[str, Any]) -> None:
        self._client = client
        self.slot: str
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._display_icon: str = data['displayIcon']

    def __repr__(self) -> str:
        return f'<AgentAbility display_name={self.display_name!r}>'

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent role's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the agent role's name."""
        return self.name_localizations.american_english

    @property
    def description_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent role's descriptions."""
        return Localization(self._description, locale=self._client.locale)

    @property
    def description(self) -> str:
        """:class: `str` Returns the agent role's description."""
        return self.description_localizations.american_english

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the agent role's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)


class AgentMedia:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.id: int = data['id']
        self.wwise: str = data['wwise']
        self.wave: str = data['wave']


class AgentVoiceLine:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.min_duration: float = data['minDuration']
        self.max_duration: float = data['maxDuration']
        self.media_list: List[AgentMedia] = [AgentMedia(media) for media in data['mediaList']]


class AgentVoiceLineLocalization:
    def __init__(
        self,
        untranslated: Dict[str, Any],
        locale: Union[str, Locale] = None,
    ) -> None:
        self.untranslated = untranslated
        self._locale = locale

        # locale code
        self.ar_AE: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('ar-AE')) if self.untranslated.get('ar-AE') else None
        )
        self.de_DE: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('de-DE')) if self.untranslated.get('de-DE') else None
        )
        self.en_US: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('en-US')) if self.untranslated.get('en-US') else None
        )
        self.es_ES: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('es-ES')) if self.untranslated.get('es-ES') else None
        )
        self.es_MX: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('es-MX')) if self.untranslated.get('es-MX') else None
        )
        self.fr_FR: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('fr-FR')) if self.untranslated.get('fr-FR') else None
        )
        self.id_ID: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('id-ID')) if self.untranslated.get('id-ID') else None
        )
        self.it_IT: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('it-IT')) if self.untranslated.get('it-IT') else None
        )
        self.ja_JP: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('ja-JP')) if self.untranslated.get('ja-JP') else None
        )
        self.ko_KR: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('ko-KR')) if self.untranslated.get('ko-KR') else None
        )
        self.pl_PL: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('pl-PL')) if self.untranslated.get('pl-PL') else None
        )
        self.pt_BR: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('pt-BR')) if self.untranslated.get('pt-BR') else None
        )
        self.ru_RU: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('ru-RU')) if self.untranslated.get('ru-RU') else None
        )
        self.th_TH: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('th-TH')) if self.untranslated.get('th-TH') else None
        )
        self.tr_TR: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('tr-TR')) if self.untranslated.get('tr-TR') else None
        )
        self.vi_VN: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('vi-VN')) if self.untranslated.get('vi-VN') else None
        )
        self.zh_CN: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('zh-CN')) if self.untranslated.get('zh-CN') else None
        )
        self.zh_TW: AgentVoiceLine = (
            AgentVoiceLine(self.untranslated.get('zh-TW')) if self.untranslated.get('zh-TW') else None
        )

        # locale language
        self.arabic: AgentVoiceLine = self.ar_AE
        self.german: AgentVoiceLine = self.de_DE
        self.english: AgentVoiceLine = self.en_US
        self.american_english: AgentVoiceLine = self.en_US
        self.british_english: AgentVoiceLine = self.en_US
        self.spanish: AgentVoiceLine = self.es_ES
        self.spanish_mexican: AgentVoiceLine = self.es_MX
        self.french: AgentVoiceLine = self.fr_FR
        self.indonesian: AgentVoiceLine = self.id_ID
        self.italian: AgentVoiceLine = self.it_IT
        self.japanese: AgentVoiceLine = self.ja_JP
        self.korean: AgentVoiceLine = self.ko_KR
        self.polish: AgentVoiceLine = self.pl_PL
        self.portuguese_brazil: AgentVoiceLine = self.pt_BR
        self.russian: AgentVoiceLine = self.ru_RU
        self.thai: AgentVoiceLine = self.th_TH
        self.turkish: AgentVoiceLine = self.tr_TR
        self.vietnamese: AgentVoiceLine = self.vi_VN
        self.chinese_simplified: AgentVoiceLine = self.zh_CN
        self.chinese_traditional: AgentVoiceLine = self.zh_TW

    def __repr__(self) -> str:
        return f'<AgentVoiceLineLocalization untranslated={self.untranslated!r}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Localization) and self.untranslated == other.untranslated

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.untranslated)


class Agent(BaseModel):
    def __init__(self, client: Client, data: Optional[Dict[str, Any]]) -> None:
        super().__init__(client=client, data=data)

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<Agent display_name={self.display_name!r}>'

    def _update(self, data: Optional[Any]) -> None:
        self._uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._description: Union[str, Dict[str, str]] = data['description']
        self.developer_name: str = data['developerName']
        self.character_tags: Optional[str] = data['characterTags']
        self._display_icon: str = data['displayIcon']
        self._display_icon_small: str = data['displayIconSmall']
        self._bust_portrait: Optional[str] = data['bustPortrait']
        self._full_portrait: Optional[str] = data['fullPortrait']
        self._full_portrait_v2: Optional[str] = data['fullPortraitV2']
        self._killfeed_portrait: str = data['killfeedPortrait']
        self.background: Optional[str] = data['background']
        self.background_gradient_colors: List[str] = data['backgroundGradientColors']
        self._is_full_portrait_right_facing: bool = data['isFullPortraitRightFacing']
        self._is_playable_character: bool = data['isPlayableCharacter']
        self._is_available_for_test: bool = data['isAvailableForTest']
        self._is_base_content: bool = data['isBaseContent']
        self.role: AgentRole = AgentRole(client=self._client, data=data['role'])
        self.abilities: Optional[List[AgentAbility]] = (
            [AgentAbility(client=self._client, data=ability) for ability in data['abilities']]
            if data.get('abilities')
            else None
        )
        self._voice_line: Dict[str, Any] = data['voiceLine']

    @property
    def name_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's names."""
        return Localization(self._display_name, locale=self._client.locale)

    @property
    def display_name(self) -> str:
        """:class: `str` Returns the agent's name."""
        return self.name_localizations.american_english

    @property
    def description_localizations(self) -> Localization:
        """:class: `Localization` Returns the agent's descriptions."""
        return Localization(self._description, locale=self._client.locale)

    @property
    def description(self) -> str:
        """:class: `str` Returns the agent's description."""
        return self.description_localizations.american_english

    @property
    def display_icon(self) -> Asset:
        """:class: `Asset` Returns the agent's display icon."""
        return Asset._from_url(client=self._client, url=self._display_icon)

    @property
    def display_icon_small(self) -> Asset:
        """:class: `Asset` Returns the agent's display icon small."""
        return Asset._from_url(client=self._client, url=self._display_icon_small)

    @property
    def bust_portrait(self) -> Optional[Asset]:
        """:class: `Asset` Returns the agent's bust portrait."""
        return Asset._from_url(client=self._client, url=self._bust_portrait) if self._bust_portrait else None

    @property
    def full_portrait(self) -> Optional[Asset]:
        """:class: `Asset` Returns the agent's full portrait."""
        return Asset._from_url(client=self._client, url=self._full_portrait) if self._full_portrait else None

    @property
    def full_portrait_v2(self) -> Optional[Asset]:
        """:class: `Asset` Returns the agent's full portrait v2."""
        return Asset._from_url(client=self._client, url=self._full_portrait_v2) if self._full_portrait_v2 else None

    @property
    def killfeed_portrait(self) -> Asset:
        """:class: `Asset` Returns the agent's killfeed portrait."""
        return Asset._from_url(client=self._client, url=self._killfeed_portrait)

    def is_full_portrait_right_facing(self) -> bool:
        """:class: `bool` Returns whether the agent's full portrait is right facing."""
        return self._is_full_portrait_right_facing

    def is_playable_character(self) -> bool:
        """Returns whether the agent is playable."""
        return self._is_playable_character

    def is_available_for_test(self) -> bool:
        """Returns whether the agent is available for test."""
        return self._is_available_for_test

    def is_base_content(self) -> bool:
        """Returns whether the agent is base content."""
        return self._is_base_content

    @classmethod
    def _from_uuid(cls, client: Client, uuid: str) -> Optional[Self]:
        """Returns the agent with the given UUID."""
        data = client.assets.get_agent(uuid)
        return cls(client=client, data=data) if data else None
