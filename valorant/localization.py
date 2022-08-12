from __future__ import annotations

from .enums import Locale
from typing import Dict, Union

__all__ = ("Localization",)

class Localization:

    def __init__(self, untranslated: Union[str, Dict[str, str]], locale: Union[str, Locale] = None) -> None:
        self.untranslated = untranslated

    def __repr__(self) -> str:
        return f'<Translator untranslated={self.untranslated!r}>'

    def __str__(self) -> str:
        """Returns the default locale."""
        return self.english

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Localization) and self.untranslated == other.untranslated

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.untranslated)

    @property
    def arabic(self) -> str:
        """:class:`str`: Returns the arabic locale."""
        return self.untranslated['ar-AE'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def german(self) -> str:
        """:class:`str`: Returns the german locale."""
        return self.untranslated['de-DE'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def english(self) -> str:
        """:class:`str`: Returns the english locale."""
        return self.untranslated['en-US'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def american_english(self) -> str:
        """:class:`str`: Returns the american english locale."""
        return self.untranslated['en-US'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def british_english(self) -> str:
        """:class:`str`: Returns the british english locale."""
        return self.untranslated['en-US'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def spanish(self) -> str:
        """:class:`str`: Returns the spanish locale."""
        return self.untranslated['es-ES'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def spanish_mexico(self) -> str:
        """:class:`str`: Returns the spanish mexico locale."""
        return self.untranslated['es-MX'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def french(self) -> str:
        """:class:`str`: Returns the french locale."""
        return self.untranslated['fr-FR'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def indonesian(self) -> str:
        """:class:`str`: Returns the indonesian locale."""
        return self.untranslated['id-ID'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def italian(self) -> str:
        """:class:`str`: Returns the italian locale."""
        return self.untranslated['it-IT'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def japanese(self) -> str:
        """:class:`str`: Returns the japanese locale."""
        return self.untranslated['ja-JP'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def korean(self) -> str:
        """:class:`str`: Returns the korean locale."""
        return self.untranslated['ko-KR'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def polish(self) -> str:
        """:class:`str`: Returns the polish locale."""
        return self.untranslated['pl-PL'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def portuguese_brazil(self) -> str:
        """:class:`str`: Returns the portuguese brazil locale."""
        return self.untranslated['pt-BR'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def russian(self) -> str:
        """:class:`str`: Returns the russian locale."""
        return self.untranslated['ru-RU'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def thai(self) -> str:
        """:class:`str`: Returns the thai locale."""
        return self.untranslated['th-TH'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def turkish(self) -> str:
        """:class:`str`: Returns the turkish locale."""
        return self.untranslated['tr-TR'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def vietnamese(self) -> str:
        """:class:`str`: Returns the vietnamese locale."""
        return self.untranslated['vi-VN'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def chinese(self) -> str:
        """:class:`str`: Returns the chinese locale."""
        return self.untranslated['zh-CN'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def chinese_traditional(self) -> str:
        """:class:`str`: Returns the chinese traditional locale."""
        return self.untranslated['zh-TW'] if isinstance(self.untranslated, dict) else self.untranslated

    @property
    def default(self) -> str:
        """:class:`str`: Returns the english locale is default."""
        return self.english

    @property
    def locale(self) -> str:
        """ :class:`str`: Returns from your current locale."""
        return getattr(self, self.untranslated, self.english)

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
