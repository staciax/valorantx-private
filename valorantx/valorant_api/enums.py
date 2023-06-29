"""
Enums functions: https://github.com/Rapptz/discord.py/blob/master/discord/enums.py

"""

from __future__ import annotations

import types
from collections import namedtuple
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Iterator, List, Mapping, Optional, Tuple, Type, TypeVar

# -- https://github.com/Rapptz/discord.py/blob/master/discord/enums.py


def _create_value_cls(name: str, comparable: bool):
    # All the type ignores here are due to the type checker being unable to recognise
    # Runtime type creation without exploding.
    cls = namedtuple('_EnumValue_' + name, 'name value')
    cls.__repr__ = lambda self: f'<{name}.{self.name}: {self.value!r}>'  # type: ignore
    cls.__str__ = lambda self: f'{name}.{self.name}'  # type: ignore
    if comparable:
        cls.__le__ = lambda self, other: isinstance(other, self.__class__) and self.value <= other.value  # type: ignore
        cls.__ge__ = lambda self, other: isinstance(other, self.__class__) and self.value >= other.value  # type: ignore
        cls.__lt__ = lambda self, other: isinstance(other, self.__class__) and self.value < other.value  # type: ignore
        cls.__gt__ = lambda self, other: isinstance(other, self.__class__) and self.value > other.value  # type: ignore
    return cls


def _is_descriptor(obj):
    return hasattr(obj, '__get__') or hasattr(obj, '__set__') or hasattr(obj, '__delete__')


class EnumMeta(type):
    if TYPE_CHECKING:
        __name__: ClassVar[str]
        _enum_member_names_: ClassVar[List[str]]
        _enum_member_map_: ClassVar[Dict[str, Any]]
        _enum_value_map_: ClassVar[Dict[Any, Any]]
        _enum_string_key_map_: ClassVar[Dict[str, Any]]

    def __new__(cls, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any], *, comparable: bool = False) -> Self:
        value_mapping = {}
        string_key_mapping = {}
        member_mapping = {}
        member_names = []

        value_cls = _create_value_cls(name, comparable)
        for key, value in list(attrs.items()):
            is_descriptor = _is_descriptor(value)
            if key[0] == '_' and not is_descriptor:
                continue

            # Special case classmethod to just pass through
            if isinstance(value, classmethod):
                continue

            if is_descriptor:
                setattr(value_cls, key, value)
                del attrs[key]
                continue

            try:
                new_value = value_mapping[value]
            except KeyError:
                new_value = value_cls(name=key, value=value)
                value_mapping[value] = new_value
                member_names.append(key)

            try:
                string_key_mapping[value]
            except KeyError:
                string_key_mapping[str(key)] = value_cls(name=key, value=value)

            member_mapping[key] = new_value
            attrs[key] = new_value

        attrs['_enum_value_map_'] = value_mapping
        attrs['_enum_string_key_map_'] = string_key_mapping
        attrs['_enum_member_map_'] = member_mapping
        attrs['_enum_member_names_'] = member_names
        attrs['_enum_value_cls_'] = value_cls
        actual_cls = super().__new__(cls, name, bases, attrs)
        value_cls._actual_enum_cls_ = actual_cls  # type: ignore # Runtime attribute isn't understood
        return actual_cls

    def __iter__(cls) -> Iterator[Any]:
        return (cls._enum_member_map_[name] for name in cls._enum_member_names_)

    def __reversed__(cls) -> Iterator[Any]:
        return (cls._enum_member_map_[name] for name in reversed(cls._enum_member_names_))

    def __len__(cls) -> int:
        return len(cls._enum_member_names_)

    def __repr__(cls) -> str:
        return f'<enum {cls.__name__}>'

    @property
    def __members__(cls) -> Mapping[str, Any]:
        return types.MappingProxyType(cls._enum_member_map_)

    def __call__(cls, value: str) -> Any:
        try:
            return cls._enum_value_map_[value]
        except (KeyError, TypeError):
            raise ValueError(f"{value!r} is not a valid {cls.__name__}")

    def __getitem__(cls, key: str) -> Any:
        return cls._enum_member_map_[key]

    def __setattr__(cls, name: str, value: Any) -> None:
        raise TypeError('Enums are immutable.')

    def __delattr__(cls, attr: str) -> None:
        raise TypeError('Enums are immutable')

    def __instancecheck__(self, instance: Any) -> bool:
        # isinstance(x, Y)
        # -> __instancecheck__(Y, x)
        try:
            return instance._actual_enum_cls_ is self
        except AttributeError:
            return False


if TYPE_CHECKING:
    from enum import Enum

    from typing_extensions import Self
else:

    class Enum(metaclass=EnumMeta):
        @classmethod
        def try_value(cls, value):
            try:
                return cls._enum_value_map_[value]
            except (KeyError, TypeError):
                return value


# --

__all__ = (
    'AbilityType',
    'EMPTY_TITLE_ID',
    'ItemTypeID',
    'Locale',
    'MELEE_WEAPON_ID',
    'MissionType',
    'RelationType',
    'RewardType',
    'try_enum',
)


EMPTY_TITLE_ID: str = 'd13e579c-435e-44d4-cec2-6eae5a3c5ed4'
MELEE_WEAPON_ID: str = '2f59173c-4bed-b6c3-2191-dea9b58be9c7'


class AbilityType(Enum):
    passive = 'Passive'
    grenade = 'Grenade'
    ability_1 = 'Ability1'
    ability_2 = 'Ability2'
    ultimate = 'Ultimate'


class ItemTypeID(Enum):
    agent = '01bb38e1-da47-4e6a-9b3d-945fe4655707'
    buddy = 'buddy'  # unknown type
    buddy_level = 'dd3bf334-87f3-40bd-b043-682a57a8dc3a'
    contract = 'f85cb6f7-33e5-4dc8-b609-ec7212301948'
    skin = 'skin'  # unknown type
    skin_level = 'e7c63390-eda7-46e0-bb7a-a6abdacd2433'
    skin_chroma = '3ad1b2b2-acdb-4524-852f-954a76ddae0a'
    spray = 'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475'
    spray_level = 'spray_level'  # unknown type
    player_card = '3f296c07-64c3-494c-923b-fe692a4fa1bd'
    player_title = 'de7caa6b-adf7-4588-bbd1-143831e786c6'
    weapon = 'weapon'  # unknown type
    level_border = 'level_border'  # unknown type
    currency = 'ea6fcd2e-8373-4137-b1c0-b458947aa86d'
    weapon_skin = 'bcef87d6-209b-46c6-8b19-fbe40bd95abc'

    def __str__(self) -> str:
        return str(self.value)


class RelationType(Enum):
    agent = 'Agent'
    event = 'Event'
    season = 'Season'

    def __str__(self) -> str:
        return str(self.value)


class RewardType(Enum):
    skin_level = 'EquippableSkinLevel'
    buddy_level = 'EquippableCharmLevel'
    currency = 'Currency'
    player_card = 'PlayerCard'
    player_title = 'Title'
    spray = 'Spray'
    agent = 'Character'

    def __str__(self) -> str:
        return str(self.value)


class MissionType(Enum):
    weekly = 'Weekly'
    daily = 'Daily'
    tutorial = 'Tutorial'
    npe = 'NPE'

    def __str__(self) -> str:
        return str(self.value)

    @property
    def full(self) -> str:
        return f'AresMissionType::{self.value}'


# class SeasonType(Enum):
#     episode = 'episode'
#     act = 'act'


class Locale(Enum):
    arabic = 'ar-AE'
    german = 'de-DE'
    american_english = 'en-US'
    british_english = 'en-US'
    spain_spanish = 'es-ES'
    spanish_mexican = 'es-MX'
    french = 'fr-FR'
    indonesian = 'id-ID'
    italian = 'it-IT'
    japanese = 'ja-JP'
    korean = 'ko-KR'
    polish = 'pl-PL'
    brazil_portuguese = 'pt-BR'
    russian = 'ru-RU'
    thai = 'th-TH'
    turkish = 'tr-TR'
    vietnamese = 'vi-VN'
    chinese = 'zh-CN'
    taiwan_chinese = 'zh-TW'

    # aliases
    english = 'en-US'

    def __str__(self) -> str:
        return str(self.value)


# from discord.py
# https://github.com/Rapptz/discord.py/blob/master/discord/enums.py

E = TypeVar('E', bound='Enum')


def create_unknown_value(cls: Type[E], val: Any) -> E:
    value_cls = cls._enum_value_cls_  # type: ignore # This is narrowed below
    name = f'unknown_{val}'
    return value_cls(name=name, value=val)


def try_enum(cls: Type[E], val: Any, default: Optional[Any] = None) -> E:
    """A function that tries to turn the value into enum ``cls``.

    If it fails it returns a proxy invalid value instead.
    """
    try:
        return cls._enum_value_map_[val]  # type: ignore # All errors are caught below
    except (KeyError, TypeError, AttributeError):
        if default is not None:
            return default
        return create_unknown_value(cls, val)


# ---
