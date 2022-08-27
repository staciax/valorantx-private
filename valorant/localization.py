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

from typing import Dict, Union

from .enums import Locale

__all__ = ("Localization",)


class Localization:
    def __init__(
        self,
        untranslated: Union[str, Dict[str, str]],
        locale: Union[str, Locale] = None,
    ) -> None:
        self.untranslated = untranslated
        self._locale = locale

        # locale code
        self.ar_AE: str = self.untranslated.get('ar-AE', self.default)
        self.de_DE: str = self.untranslated.get('de-DE', self.default)
        self.en_US: str = self.untranslated.get('en-US', self.default)
        self.es_ES: str = self.untranslated.get('es-ES', self.default)
        self.es_MX: str = self.untranslated.get('es-MX', self.default)
        self.fr_FR: str = self.untranslated.get('fr-FR', self.default)
        self.id_ID: str = self.untranslated.get('id-ID', self.default)
        self.it_IT: str = self.untranslated.get('it-IT', self.default)
        self.ja_JP: str = self.untranslated.get('ja-JP', self.default)
        self.ko_KR: str = self.untranslated.get('ko-KR', self.default)
        self.pl_PL: str = self.untranslated.get('pl-PL', self.default)
        self.pt_BR: str = self.untranslated.get('pt-BR', self.default)
        self.ru_RU: str = self.untranslated.get('ru-RU', self.default)
        self.th_TH: str = self.untranslated.get('th-TH', self.default)
        self.tr_TR: str = self.untranslated.get('tr-TR', self.default)
        self.vi_VN: str = self.untranslated.get('vi-VN', self.default)
        self.zh_CN: str = self.untranslated.get('zh-CN', self.default)
        self.zh_TW: str = self.untranslated.get('zh-TW', self.default)

        # locale language
        self.arabic: str = self.ar_AE
        self.german: str = self.de_DE
        self.english: str = self.en_US
        self.american_english: str = self.en_US
        self.british_english: str = self.en_US
        self.spanish: str = self.es_ES
        self.spanish_mexican: str = self.es_MX
        self.french: str = self.fr_FR
        self.indonesian: str = self.id_ID
        self.italian: str = self.it_IT
        self.japanese: str = self.ja_JP
        self.korean: str = self.ko_KR
        self.polish: str = self.pl_PL
        self.portuguese_brazil: str = self.pt_BR
        self.russian: str = self.ru_RU
        self.thai: str = self.th_TH
        self.turkish: str = self.tr_TR
        self.vietnamese: str = self.vi_VN
        self.chinese_simplified: str = self.zh_CN
        self.chinese_traditional: str = self.zh_TW

    def __repr__(self) -> str:
        return f'<Translator untranslated={self.untranslated!r}>'

    def __str__(self) -> str:
        """Returns the default locale."""
        return self.locale

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Localization) and self.untranslated == other.untranslated

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.untranslated)

    @property
    def default(self) -> str:
        """:class:`str`: Returns the english locale is default."""
        if isinstance(self.untranslated, str):
            return self.untranslated
        return self.untranslated.get('en-US')

    @property
    def locale(self) -> str:
        """:class:`str`: Returns from your current locale."""
        return self.untranslated.get(str(self._locale), self.default)

    def from_locale_code(self, value: str):
        """:class:`str`: Returns the locale from the locale code."""
        locale = getattr(self, value.lower())
        if locale is None:
            raise ValueError("Unknown locale.")
        return locale
