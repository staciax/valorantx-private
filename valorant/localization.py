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

from typing import Dict, Optional, Union

from .enums import Locale

__all__ = ("Localization",)


class Localization:
    def __init__(
        self,
        untranslated: Optional[Union[str, Dict[str, str]]],
        locale: Union[str, Locale] = None,
    ) -> None:
        self.untranslated = untranslated
        self._locale = locale
        if self.untranslated is None:
            self.untranslated = {}
        self.ar_AE: str = self.untranslated.get('ar-AE', self.untranslated)
        self.de_DE: str = self.untranslated.get('de-DE', self.untranslated)
        self.en_US: str = self.untranslated.get('en-US', self.untranslated)
        self.es_ES: str = self.untranslated.get('es-ES', self.untranslated)
        self.es_MX: str = self.untranslated.get('es-MX', self.untranslated)
        self.fr_FR: str = self.untranslated.get('fr-FR', self.untranslated)
        self.id_ID: str = self.untranslated.get('id-ID', self.untranslated)
        self.it_IT: str = self.untranslated.get('it-IT', self.untranslated)
        self.ja_JP: str = self.untranslated.get('ja-JP', self.untranslated)
        self.ko_KR: str = self.untranslated.get('ko-KR', self.untranslated)
        self.pl_PL: str = self.untranslated.get('pl-PL', self.untranslated)
        self.pt_BR: str = self.untranslated.get('pt-BR', self.untranslated)
        self.ru_RU: str = self.untranslated.get('ru-RU', self.untranslated)
        self.th_TH: str = self.untranslated.get('th-TH', self.untranslated)
        self.tr_TR: str = self.untranslated.get('tr-TR', self.untranslated)
        self.vi_VN: str = self.untranslated.get('vi-VN', self.untranslated)
        self.zh_CN: str = self.untranslated.get('zh-CN', self.untranslated)
        self.zh_TW: str = self.untranslated.get('zh-TW', self.untranslated)

    def __repr__(self) -> str:
        if self.default is None:
            return ''
        return f'<Translator default={self.default!r}>'

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
    def arabic(self) -> str:
        """:class:`str`: Returns the Arabic locale."""
        return self.ar_AE

    @property
    def german(self) -> str:
        """:class:`str`: Returns the German locale."""
        return self.de_DE

    @property
    def english(self) -> str:
        """:class:`str`: Returns the English locale."""
        return self.en_US

    @property
    def american_english(self) -> str:
        """:class:`str`: Returns the American English locale."""
        return self.en_US

    @property
    def british_english(self) -> str:
        """:class:`str`: Returns the British English locale."""
        return self.en_US

    @property
    def spanish(self) -> str:
        """:class:`str`: Returns the Spanish locale."""
        return self.es_ES

    @property
    def spanish_mexican(self) -> str:
        """:class:`str`: Returns the Spanish Mexican locale."""
        return self.es_MX

    @property
    def french(self) -> str:
        """:class:`str`: Returns the French locale."""
        return self.fr_FR

    @property
    def indonesian(self) -> str:
        """:class:`str`: Returns the Indonesian locale."""
        return self.id_ID

    @property
    def italian(self) -> str:
        """:class:`str`: Returns the Italian locale."""
        return self.it_IT

    @property
    def japanese(self) -> str:
        """:class:`str`: Returns the Japanese locale."""
        return self.ja_JP

    @property
    def korean(self) -> str:
        """:class:`str`: Returns the Korean locale."""
        return self.ko_KR

    @property
    def polish(self) -> str:
        """:class:`str`: Returns the Polish locale."""
        return self.pl_PL

    @property
    def portuguese_brazil(self) -> str:
        """:class:`str`: Returns the Portuguese Brazil locale."""
        return self.pt_BR

    @property
    def russian(self) -> str:
        """:class:`str`: Returns the Russian locale."""
        return self.ru_RU

    @property
    def thai(self) -> str:
        """:class:`str`: Returns the Thai locale."""
        return self.th_TH

    @property
    def turkish(self) -> str:
        """:class:`str`: Returns the Turkish locale."""
        return self.tr_TR

    @property
    def vietnamese(self) -> str:
        """:class:`str`: Returns the Vietnamese locale."""
        return self.vi_VN

    @property
    def chinese_simplified(self) -> str:
        """:class:`str`: Returns the Chinese Simplified locale."""
        return self.zh_CN

    @property
    def chinese_traditional(self) -> str:
        """:class:`str`: Returns the Chinese Traditional locale."""
        return self.zh_TW

    @property
    def default(self) -> str:
        """:class:`str`: Returns the english locale is default."""
        if isinstance(self.untranslated, str):
            return self.untranslated
        elif isinstance(self.untranslated, dict):
            return self.untranslated.get('en-US', '')
        else:
            return ''

    @property
    def locale(self) -> str:
        """:class:`str`: Returns from your current locale."""
        return self.untranslated.get(str(self._locale), self.default)

    def from_locale_code(self, value: str):
        """:class:`str`: Returns the locale from the locale code."""
        try:
            locale = getattr(self, value.replace('-', '_'))
        except AttributeError:
            locale = self.untranslated.get(value, self.default)
        return locale
