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


class Role:
    def __init__(self, client: Client, data: Dict[str, Any]) -> None:
        self._client = client
        self.uuid: str = data['uuid']
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._display_icon: Optional[str] = data['displayIcon']
        self.asset_path: str = data['assetPath']

    def __repr__(self) -> str:
        return f'<Role display_name={self.display_name!r}>'

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


class Ability:
    def __init__(self, client: Client, data: Dict[str, Any]) -> None:
        self._client = client
        self.slot: str
        self._display_name: Union[str, Dict[str, str]] = data['displayName']
        self._description: Union[str, Dict[str, str]] = data['description']
        self._display_icon: str = data['displayIcon']

    def __repr__(self) -> str:
        return f'<Ability display_name={self.display_name!r}>'

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


class Media:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.id: int = data['id']
        self.wwise: str = data['wwise']
        self.wave: str = data['wave']

    def __repr__(self) -> str:
        return f'<Media id={self.id!r} wwise={self.wwise!r} wave={self.wave!r}>'


class VoiceLine:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.min_duration: float = data['minDuration']
        self.max_duration: float = data['maxDuration']
        self.media_list: List[Media] = [Media(media) for media in data['mediaList']]

    def __repr__(self) -> str:
        return f'<AgentVoiceLine min_duration={self.min_duration!r} max_duration={self.max_duration!r}>'


class VoiceLineLocalization:
    def __init__(
        self,
        untranslated: Dict[str, Any],
        locale: Union[str, Locale] = None,
    ) -> None:
        self.untranslated = untranslated
        self._locale = locale

        # locale code
        self.ar_AE: VoiceLine = VoiceLine(self.untranslated.get('ar-AE')) if self.untranslated.get('ar-AE') else None
        self.de_DE: VoiceLine = VoiceLine(self.untranslated.get('de-DE')) if self.untranslated.get('de-DE') else None
        self.en_US: VoiceLine = VoiceLine(self.untranslated.get('en-US')) if self.untranslated.get('en-US') else None
        self.es_ES: VoiceLine = VoiceLine(self.untranslated.get('es-ES')) if self.untranslated.get('es-ES') else None
        self.es_MX: VoiceLine = VoiceLine(self.untranslated.get('es-MX')) if self.untranslated.get('es-MX') else None
        self.fr_FR: VoiceLine = VoiceLine(self.untranslated.get('fr-FR')) if self.untranslated.get('fr-FR') else None
        self.id_ID: VoiceLine = VoiceLine(self.untranslated.get('id-ID')) if self.untranslated.get('id-ID') else None
        self.it_IT: VoiceLine = VoiceLine(self.untranslated.get('it-IT')) if self.untranslated.get('it-IT') else None
        self.ja_JP: VoiceLine = VoiceLine(self.untranslated.get('ja-JP')) if self.untranslated.get('ja-JP') else None
        self.ko_KR: VoiceLine = VoiceLine(self.untranslated.get('ko-KR')) if self.untranslated.get('ko-KR') else None
        self.pl_PL: VoiceLine = VoiceLine(self.untranslated.get('pl-PL')) if self.untranslated.get('pl-PL') else None
        self.pt_BR: VoiceLine = VoiceLine(self.untranslated.get('pt-BR')) if self.untranslated.get('pt-BR') else None
        self.ru_RU: VoiceLine = VoiceLine(self.untranslated.get('ru-RU')) if self.untranslated.get('ru-RU') else None
        self.th_TH: VoiceLine = VoiceLine(self.untranslated.get('th-TH')) if self.untranslated.get('th-TH') else None
        self.tr_TR: VoiceLine = VoiceLine(self.untranslated.get('tr-TR')) if self.untranslated.get('tr-TR') else None
        self.vi_VN: VoiceLine = VoiceLine(self.untranslated.get('vi-VN')) if self.untranslated.get('vi-VN') else None
        self.zh_CN: VoiceLine = VoiceLine(self.untranslated.get('zh-CN')) if self.untranslated.get('zh-CN') else None
        self.zh_TW: VoiceLine = VoiceLine(self.untranslated.get('zh-TW')) if self.untranslated.get('zh-TW') else None

        # locale language
        self.arabic: VoiceLine = self.ar_AE
        self.german: VoiceLine = self.de_DE
        self.english: VoiceLine = self.en_US
        self.american_english: VoiceLine = self.en_US
        self.british_english: VoiceLine = self.en_US
        self.spanish: VoiceLine = self.es_ES
        self.spanish_mexican: VoiceLine = self.es_MX
        self.french: VoiceLine = self.fr_FR
        self.indonesian: VoiceLine = self.id_ID
        self.italian: VoiceLine = self.it_IT
        self.japanese: VoiceLine = self.ja_JP
        self.korean: VoiceLine = self.ko_KR
        self.polish: VoiceLine = self.pl_PL
        self.portuguese_brazil: VoiceLine = self.pt_BR
        self.russian: VoiceLine = self.ru_RU
        self.thai: VoiceLine = self.th_TH
        self.turkish: VoiceLine = self.tr_TR
        self.vietnamese: VoiceLine = self.vi_VN
        self.chinese_simplified: VoiceLine = self.zh_CN
        self.chinese_traditional: VoiceLine = self.zh_TW

    def __repr__(self) -> str:
        attrs = [
            ('ar_AE', self.ar_AE),
            ('de_DE', self.de_DE),
            ('en_US', self.en_US),
            ('es_ES', self.es_ES),
            ('es_MX', self.es_MX),
            ('fr_FR', self.fr_FR),
            ('id_ID', self.id_ID),
            ('it_IT', self.it_IT),
            ('ja_JP', self.ja_JP),
            ('ko_KR', self.ko_KR),
            ('pl_PL', self.pl_PL),
            ('pt_BR', self.pt_BR),
            ('ru_RU', self.ru_RU),
            ('th_TH', self.th_TH),
            ('tr_TR', self.tr_TR),
            ('vi_VN', self.vi_VN),
            ('zh_CN', self.zh_CN),
            ('zh_TW', self.zh_TW),
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

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
        self._role: Dict[str, str] = data['role']
        self._abilities: List[Dict[Any, Any]] = data.get('abilities', [])
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

    @property
    def role(self) -> Role:
        """:class: `AgentRole` Returns the agent's role."""
        return Role(client=self._client, data=self._role)

    @property
    def abilities(self) -> List[Ability]:
        """:class: `List[AgentAbility]` Returns the agent's abilities."""
        return [Ability(client=self._client, data=ability) for ability in self._abilities]

    @property
    def voice_line(self) -> VoiceLineLocalization:
        """:class: `AgentVoiceLineLocalization` Returns the agent's voice line."""
        return VoiceLineLocalization(self._voice_line)

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
