from __future__ import annotations

import types
from collections import namedtuple
from typing import (
    Any,
    Dict,
    ClassVar,
    List,
    Optional,
    Mapping,
    Iterator,
    Type,
    TypeVar,
    Tuple,
    TYPE_CHECKING
)

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
                new_value = value_mapping[value] or string_key_mapping[value]
            except KeyError:
                new_value = value_cls(name=key, value=value)
                value_mapping[value] = new_value
                string_key_mapping[str(key)] = value_cls(name=key, value=value)
                member_names.append(key)

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

EmptyTitle = 'd13e579c-435e-44d4-cec2-6eae5a3c5ed4'

__all__ = (
    'Region',
    'Shard',
    'ItemType',
    'AgentID',
    'QueueID',
    'MapID',
    'WeaponID',
    'CurrencyID',
    'SpraySlotID',
    'Locale',
    'try_enum',
    'try_enum_key'
)


class Region(Enum):
    NA = 'na'
    EU = 'eu'
    LATAM = 'latam'
    BR = 'br'
    AP = 'ap'
    KR = 'kr'
    PBE = 'pbe'

    def __str__(self) -> str:
        return self._region_shard_override()

    @property
    def shard(self) -> str:
        return getattr(Shard, self.value.upper())

    def _region_shard_override(self) -> str:
        if self.shard is self.PBE.value:
            return self.NA.value
        return self.value

class Shard(Enum):
    NA = 'na'
    EU = 'eu'
    LATAM = 'na'
    BR = 'na'
    AP = 'ap'
    KR = 'kr'
    PBE = 'pbe'

    def __str__(self) -> str:
        return self.value

class ItemType(Enum):
    agent = '01bb38e1-da47-4e6a-9b3d-945fe4655707'
    buddy = 'dd3bf334-87f3-40bd-b043-682a57a8dc3a'
    contract = 'f85cb6f7-33e5-4dc8-b609-ec7212301948'
    skin = 'e7c63390-eda7-46e0-bb7a-a6abdacd2433'
    skin_chroma = '3ad1b2b2-acdb-4524-852f-954a76ddae0a'
    spray = 'd5f120f8-ff8c-4aac-92ea-f2b5acbe9475'
    player_card = '3f296c07-64c3-494c-923b-fe692a4fa1bd'
    player_title = 'de7caa6b-adf7-4588-bbd1-143831e786c6'

    def __str__(self) -> str:
        return self.value

class AgentID(Enum):
    astra = '41fb69c1-4189-7b37-f117-bcaf1e96f1bf'
    breach = '5f8d3a7f-467b-97f3-062c-13acf203c006'
    brimstone = '9f0d8ba9-4140-b941-57d3-a7ad57c6b417'
    chamber = '22697a3d-45bf-8dd7-4fec-84a9e28c69d7'
    cypher = '117ed9e3-49f3-6512-3ccf-0cada7e3823b'
    fade = 'dade69b4-4f5a-8528-247b-219e5a1facd6'
    jett = 'add6443a-41bd-e414-f6ad-e58d267f4e95'
    kay_o = '601dbbe7-43ce-be57-2a40-4abd24953621'
    killjoy = '1e58de9c-4950-5125-93e9-a0aee9f98746'
    neon = 'bb2a4828-46eb-8cd1-e765-15848195d751'
    omen = '8e253930-4c05-31dd-1b6c-968525494517'
    phoenix = 'eb93336a-449b-9c1b-0a54-a891f7921d69'
    raze = 'f94c3b30-42be-e959-889c-5aa313dba261'
    reyna = 'a3bfb853-43b2-7238-a4f1-ad90e9e46bcc'
    sage = '569fdd95-4d10-43ab-ca70-79becc718b46'
    skye = '6f2a04ca-43e0-be17-7f36-b3908627744d'
    sova = '320b2a48-4d9b-a075-30f1-1f93a9b638fa'
    viper = '707eab51-4836-f488-046a-cda6bf494859'
    yoru = '7f94d92c-4234-0a36-9646-3a87eb8b5c89'

    def __str__(self) -> str:
        return self.value

class QueueID(Enum):
    competitive = 'competitive'
    custom = 'custom'
    deathmatch = 'deathmatch'
    escalation = 'ggteam'
    snowball = 'snowball'
    spikerush = 'spikerush'
    unrated = 'unrated'
    replication = 'onefa'
    newMap = 'newmap'

    def __str__(self) -> None:
        return self.value

    @classmethod
    def values(cls) -> List[str]:
        return [str(x) for x in cls]

class MapID(Enum):
    ascent = '7eaecc1b-4337-bbf6-6ab9-04b8f06b3319'
    bind = '2c9d57ec-4431-9c5e-2939-8f9ef6dd5cba'
    breeze = '2fb9a4fd-47b8-4e7d-a969-74b4046ebd53'
    fracture = 'b529448b-4d60-346e-e89e-00a4c527a405'
    haven = '2bee0dc9-4ffe-519b-1cbd-7fbe763a6047'
    icebox = 'e2ad5c54-4114-a870-9641-8ea21279579a'
    split = 'd960549e-485c-e861-8d71-aa9d1aed12a2'
    pearl = 'fd267378-4d1d-484f-ff52-77821ed10dc2'
    the_range = 'ee613ee9-28b7-4beb-9666-08db13bb2244'

    def __str__(self) -> str:
        return self.value

    @property
    def url(self) -> str:
        return getattr(MapURL, self.name).value

    @classmethod
    def url_to_uuid(cls, url: str) -> str:
        for x in cls:
            if x.url == url:
                return x.value
        raise ValueError(f'No map found for url {url}')

class MapURL(Enum):
    ascent = '/Game/Maps/Ascent/Ascent'
    bind = '/Game/Maps/Duality/Duality'
    breeze = '/Game/Maps/Foxtrot/Foxtrot'
    fracture = '/Game/Maps/Canyon/Canyon'
    haven = '/Game/Maps/Triad/Triad'
    icebox = '/Game/Maps/Port/Port'
    split = '/Game/Maps/Bonsai/Bonsai'
    pearl = '/Game/Maps/Pitt/Pitt'
    the_range = '/Game/Maps/Poveglia/Range'

    @property
    def uuid(self) -> str:
        return getattr(MapID, self.name).value

    @classmethod
    def uuid_to_url(cls, uuid: str) -> str:
        for x in cls:
            if x.uuid == uuid:
                return x.value
        raise ValueError(f'No map found for uuid {uuid}')

class WeaponID(Enum):

    ares = '55d8a0f4-4274-ca67-fe2c-06ab45efdf58'
    bucky = '910be174-449b-c412-ab22-d0873436b21b'
    bulldog = 'ae3de142-4d85-2547-dd26-4e90bed35cf7'
    classic = '29a0cfab-485b-f5d5-779a-b59f85e204a8'
    frenzy = '44d4e95c-4157-0037-81b2-17841bf2e8e3'
    ghost = '1baa85b4-4c70-1284-64bb-6481dfc3bb4e'
    guardian = '4ade7faa-4cf1-8376-95ef-39884480959b'
    judge = 'ec845bf4-4f79-ddda-a3da-0db3774b2794'
    marshal = 'c4883e50-4494-202c-3ec3-6b8a9284f00b'
    melee = '2f59173c-4bed-b6c3-2191-dea9b58be9c7'
    odin = '63e6c2b6-4a8e-869c-3d4c-e38355226584'
    operator = 'a03b24d3-4319-996d-0f8c-94bbfba1dfc7'
    phantom = 'ee8e8d15-496b-07ac-e5f6-8fae5d4c7b1a'
    sheriff = 'e336c6b8-418d-9340-d77f-7a9e4cfe0702'
    shorty = '42da8ccc-40d5-affc-beec-15aa47b42eda'
    spectre = '462080d1-4035-2937-7c09-27aa2a5c27a7'
    stinger = 'f7e1b454-4ad4-1063-ec0a-159e56b58941'
    vandal = '9c82e19d-4575-0200-1a81-3eacf00cf872'

    def __str__(self) -> str:
        return self.value


class CurrencyID(Enum):
    valorant_point = '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'
    radianite_point = 'e59aa87c-4cbf-517a-5983-6e81511be9b7'
    free_agent = 'f08d4ae3-939c-4576-ab26-09ce1f23bb37'

    def __str__(self) -> str:
        return self.value

class SpraySlotID(Enum):
    slot_1 = '0814b2fe-4512-60a4-5288-1fbdcec6ca48'
    slot_2 = '04af080a-4071-487b-61c0-5b9c0cfaac74'
    slot_3 = '5863985e-43ac-b05d-cb2d-139e72970014'

    def __str__(self) -> str:
        return self.value

    @classmethod
    def _from_id(cls, slot_id: str) -> int:

        if slot_id == cls.slot_1.value:
            return 1
        elif slot_id == cls.slot_2.value:
            return 2
        elif slot_id == cls.slot_3.value:
            return 3

        raise ValueError(f'Unknown slot id: {slot_id}')

class Locale(Enum):

    arabic = 'ar-AE'
    german = 'de-DE'
    american_english = 'en-US'
    british_english = 'en-US'
    spanish = 'es-ES'
    spanish_mexico = 'es-MX'
    french = 'fr-FR'
    indonesian = 'id-ID'
    italian = 'it-IT'
    japanese = 'ja-JP'
    korean = 'ko-KR'
    polish = 'pl-PL'
    portuguese = 'pt-BR'
    russian = 'ru-RU'
    thai = 'th-TH'
    turkish = 'tr-TR'
    vietnamese = 'vi-VN'
    chinese_simplified = 'zh-CN'
    chinese_traditional = 'zh-TW'

    def __str__(self) -> str:
        return self.value


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

def try_enum_key(cls: Type[E], val: Any) -> E:
    """ A function that tries to turn the value into enum ``cls``."""

    try:
        return cls._enum_string_key_map_[val]  # type: ignore # All errors are caught below
    except (KeyError, TypeError, AttributeError):
        return create_unknown_value(cls, val)


# ---
