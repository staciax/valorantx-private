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

from .enums import Locale
from typing import Dict, Union

__all__ = ("Localization",)

class Localization:
    def __init__(
        self,
        untranslated: Union[str, Dict[str, str]],
        locale: Union[str, Locale] = None,
    ) -> None:
        self.untranslated = untranslated
        self._locale = locale

    def __repr__(self) -> str:
        return f'<Translator untranslated={self.untranslated!r}>'

    def __str__(self) -> str:
        """Returns the default locale."""
        return self.english

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Localization) and self.untranslated == other.untranslated
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.untranslated)

    @property
    def arabic(self) -> str:
        """:class:`str`: Returns the arabic locale."""
        return self.untranslated['ar-AE']

    @property
    def german(self) -> str:
        """:class:`str`: Returns the german locale."""
        return self.untranslated['de-DE']

    @property
    def english(self) -> str:
        """:class:`str`: Returns the english locale."""
        return self.untranslated['en-US']

    @property
    def american_english(self) -> str:
        """:class:`str`: Returns the american english locale."""
        return self.untranslated['en-US']

    @property
    def british_english(self) -> str:
        """:class:`str`: Returns the british english locale."""
        return self.untranslated['en-US']

    @property
    def spanish(self) -> str:
        """:class:`str`: Returns the spanish locale."""
        return self.untranslated['es-ES']

    @property
    def spanish_mexico(self) -> str:
        """:class:`str`: Returns the spanish mexico locale."""
        return self.untranslated['es-MX']

    @property
    def french(self) -> str:
        """:class:`str`: Returns the french locale."""
        return self.untranslated['fr-FR']

    @property
    def indonesian(self) -> str:
        """:class:`str`: Returns the indonesian locale."""
        return self.untranslated['id-ID']

    @property
    def italian(self) -> str:
        """:class:`str`: Returns the italian locale."""
        return self.untranslated['it-IT']

    @property
    def japanese(self) -> str:
        """:class:`str`: Returns the japanese locale."""
        return self.untranslated['ja-JP']

    @property
    def korean(self) -> str:
        """:class:`str`: Returns the korean locale."""
        return self.untranslated['ko-KR']

    @property
    def polish(self) -> str:
        """:class:`str`: Returns the polish locale."""
        return self.untranslated['pl-PL']

    @property
    def portuguese_brazil(self) -> str:
        """:class:`str`: Returns the portuguese brazil locale."""
        return self.untranslated['pt-BR']

    @property
    def russian(self) -> str:
        """:class:`str`: Returns the russian locale."""
        return self.untranslated['ru-RU']

    @property
    def thai(self) -> str:
        """:class:`str`: Returns the thai locale."""
        return self.untranslated['th-TH']

    @property
    def turkish(self) -> str:
        """:class:`str`: Returns the turkish locale."""
        return self.untranslated['tr-TR']

    @property
    def vietnamese(self) -> str:
        """:class:`str`: Returns the vietnamese locale."""
        return self.untranslated['vi-VN']

    @property
    def chinese(self) -> str:
        """:class:`str`: Returns the chinese locale."""
        return self.untranslated['zh-CN']

    @property
    def chinese_traditional(self) -> str:
        """:class:`str`: Returns the chinese traditional locale."""
        return self.untranslated['zh-TW']

    @property
    def default(self) -> str:
        """:class:`str`: Returns the english locale is default."""
        return self.english

    @property
    def locale(self) -> str:
        """ :class:`str`: Returns from your current locale."""
        return self._locale

    def from_str(self, value: str):
        """Constructs a :class:`Translator` from a string."""
        locale = getattr(self, value.lower())
        if locale is None:
            raise ValueError("Unknown locale.")
        return locale

    def to_dict(self) -> Dict[str, str]:  # TODO: payload hint
        result = {
            'arabic': self.arabic,
            'german': self.german,
            'english': self.english,
            'american_english': self.american_english,
            'british_english': self.british_english,
            'spanish': self.spanish,
            'spanish_mexico': self.spanish_mexico,
            'french': self.french,
            'indonesian': self.indonesian,
            'italian': self.italian,
            'japanese': self.japanese,
            'korean': self.korean,
            'polish': self.polish,
            'portuguese_brazil': self.portuguese_brazil,
            'russian': self.russian,
            'thai': self.thai,
            'turkish': self.turkish,
            'vietnamese': self.vietnamese,
            'chinese': self.chinese,
            'chinese_traditional': self.chinese_traditional,
        }
        return result
