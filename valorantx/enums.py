# Copyright (c) 2023-present STACiA, 2021-present Rapptz
# Licensed under the MIT
# inspired by https://github.com/Rapptz/discord.py/blob/master/discord/enums.py

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, List, Optional, Tuple, Type, TypeVar

from valorant.enums import (
    AbilitySlot as AbilitySlot,
    Enum as Enum,
    Locale as Locale,
    MissionType as MissionType,
    RelationType as RelationType,
    try_enum as try_enum,
)

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    'AbilitySlot',
    'AgentID',
    'CurrencyType',
    'GameModeID',
    'GameModeURL',
    'ItemTypeID',
    'LevelBorderID',
    'Locale',
    'MapID',
    'MissionType',
    'QueueType',
    'Region',
    'RelationType',
    'RoundResultCode',
    'RoundResultType',
    'SeasonType',
    'Shard',
    'SpraySlotID',
    'WeaponID',
    'try_enum',
)


VALORANT_POINT_UUID: Final[str] = '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'
RADIANITE_POINT_UUID: Final[str] = 'e59aa87c-4cbf-517a-5983-6e81511be9b7'
KINGDOM_POINT_UUID: Final[str] = '85ca954a-41f2-ce94-9b45-8ca3dd39a00d'
CURRENCY_UUIDS: Final[Tuple[str, ...]] = (
    'f9cfa034-c7e1-4995-904c-1a296e7b1760',
    'da0edbc8-31fb-468e-95a8-27ac25cd76ed',
    'a61e8526-bb1f-4135-b7df-95e67b416efe',
)


class Region(Enum):
    AsiaPacific = 'ap'
    NorthAmerica = 'na'
    Europe = 'eu'
    LatinAmerica = 'latam'
    Brazil = 'br'
    Korea = 'kr'
    PublicBetaEnvironment = 'pbe'
    # China = '...'

    # aliases
    NA = 'na'
    EU = 'eu'
    LATAM = 'latam'
    BR = 'br'
    AP = 'ap'
    KR = 'kr'
    PBE = 'pbe'
    # CN = '...'  # TODO: Add chinese region?

    def __str__(self) -> str:
        if self.shard == 'pbe':
            return 'na'
        return str(self.value)

    @property
    def shard(self) -> str:
        if isinstance(self.value, str):
            return getattr(Shard, self.value.upper())
        return ''


class Shard(Enum):
    AsiaPacific = 'ap'
    NorthAmerica = 'na'
    Europe = 'eu'
    LatinAmerica = 'na'
    Brazil = 'na'
    Korea = 'kr'
    PublicBetaEnvironment = 'pbe'
    # China = '...'

    # aliases
    NA = 'na'
    EU = 'eu'
    LATAM = 'na'
    BR = 'na'
    AP = 'ap'
    KR = 'kr'
    PBE = 'pbe'
    # CN = '...'

    def __str__(self) -> str:
        return str(self.value)


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


class AgentID(Enum):
    astra = '41fb69c1-4189-7b37-f117-bcaf1e96f1bf'
    breach = '5f8d3a7f-467b-97f3-062c-13acf203c006'
    brimstone = '9f0d8ba9-4140-b941-57d3-a7ad57c6b417'
    chamber = '22697a3d-45bf-8dd7-4fec-84a9e28c69d7'
    cypher = '117ed9e3-49f3-6512-3ccf-0cada7e3823b'
    fade = 'dade69b4-4f5a-8528-247b-219e5a1facd6'
    deadlock = ''
    gekko = 'e370fa57-4757-3604-3648-499e1f642d3f'
    harbor = '95b78ed7-4637-86d9-7e41-71ba8c293152'
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
        return str(self.value)


class QueueType(Enum):
    competitive = 'competitive'
    custom = 'custom'
    deathmatch = 'deathmatch'
    escalation = 'ggteam'
    snowball = 'snowball'
    spikerush = 'spikerush'
    unrated = 'unrated'
    replication = 'onefa'
    newmap = 'newmap'
    swiftplay = 'swiftplay'
    team_deathmatch = 'hurm'

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def values(cls) -> List[str]:
        return [str(x) for x in cls]


class PremierEventType(Enum):
    league = 'LEAGUE'
    tournament = 'TOURNAMENT'

    def __str__(self) -> str:
        return str(self.value)


class PremierMapSelectionStrategy(Enum):
    random = 'RANDOM'
    pickban = 'PICKBAN'

    def __str__(self) -> str:
        return str(self.value)


class PremierRole(Enum):
    member = 'MEMBER'
    owner = 'OWNER'

    def __str__(self) -> str:
        return str(self.value)


class MapID(Enum):
    ascent = '7eaecc1b-4337-bbf6-6ab9-04b8f06b3319'
    bind = '2c9d57ec-4431-9c5e-2939-8f9ef6dd5cba'
    breeze = '2fb9a4fd-47b8-4e7d-a969-74b4046ebd53'
    fracture = 'b529448b-4d60-346e-e89e-00a4c527a405'
    haven = '2bee0dc9-4ffe-519b-1cbd-7fbe763a6047'
    icebox = 'e2ad5c54-4114-a870-9641-8ea21279579a'
    lotus = '2fe4ed3a-450a-948b-6d6b-e89a78e680a9'
    split = 'd960549e-485c-e861-8d71-aa9d1aed12a2'
    pearl = 'fd267378-4d1d-484f-ff52-77821ed10dc2'
    the_range = 'ee613ee9-28b7-4beb-9666-08db13bb2244'
    district = '690b3ed2-4dff-945b-8223-6da834e30d24'
    kasbah = '12452a9d-48c3-0b02-e7eb-0381c3520404'
    piazza = 'de28aa9b-4cbe-1003-320e-6cb3ec309557'

    def __str__(self) -> str:
        return str(self.value)

    @property
    def url(self) -> str:
        return getattr(MapURL, self.name).value

    @classmethod
    def from_url(cls, map_url: str) -> Self:
        for value in cls:
            if value.url == map_url:
                return value
        raise ValueError(f'No map found for url {map_url}')


class MapURL(Enum):
    ascent = '/Game/Maps/Ascent/Ascent'
    bind = '/Game/Maps/Duality/Duality'
    breeze = '/Game/Maps/Foxtrot/Foxtrot'
    fracture = '/Game/Maps/Canyon/Canyon'
    haven = '/Game/Maps/Triad/Triad'
    icebox = '/Game/Maps/Port/Port'
    lotus = '/Game/Maps/Jam/Jam'
    split = '/Game/Maps/Bonsai/Bonsai'
    pearl = '/Game/Maps/Pitt/Pitt'
    the_range = '/Game/Maps/Poveglia/Range'
    district = '/Game/Maps/HURM/HURM_Alley/HURM_Alley'
    kasbah = '/Game/Maps/HURM/HURM_Bowl/HURM_Bowl'
    piazza = '/Game/Maps/HURM/HURM_Yard/HURM_Yard'

    @property
    def id(self) -> str:
        return getattr(MapID, self.name).value

    @classmethod
    def from_id(cls, map_id: str) -> Self:
        for value in cls:
            if value.id == map_id:
                return value
        raise ValueError(f'No map found for uuid {map_id}')


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
        return str(self.value)


class GameModeURL(Enum):
    standard = '/Game/GameModes/Bomb/BombGameMode.BombGameMode_C'
    deathmatch = '/Game/GameModes/Deathmatch/DeathmatchGameMode.DeathmatchGameMode_C'
    escalation = '/Game/GameModes/GunGame/GunGameTeamsGameMode.GunGameTeamsGameMode_C'
    replication = '/Game/GameModes/OneForAll/OneForAll_GameMode.OneForAll_GameMode_C'
    spike_rush = '/Game/GameModes/QuickBomb/QuickBombGameMode.QuickBombGameMode_C'
    snowball_fight = '/Game/GameModes/SnowballFight/SnowballFightGameMode.SnowballFightGameMode_C'
    practice = '/Game/GameModes/ShootingRange/ShootingRangeGameMode.ShootingRangeGameMode_C'
    on_boarding = '/Game/GameModes/NewPlayerExperience/NPEGameMode.NPEGameMode_C'
    swiftplay = '/Game/GameModes/_Development/Swiftplay_EndOfRoundCredits/Swiftplay_EoRCredits_GameMode.Swiftplay_EoRCredits_GameMode_C'  # TODO: fix this on release

    def __str__(self) -> str:
        return str(self.value)

    @property
    def id(self) -> str:
        return getattr(GameModeID, self.name).value


class GameModeID(Enum):
    standard = '96bd3920-4f36-d026-2b28-c683eb0bcac5'
    deathmatch = 'a8790ec5-4237-f2f0-e93b-08a8e89865b2'
    escalation = 'a4ed6518-4741-6dcb-35bd-f884aecdc859'
    replication = '4744698a-4513-dc96-9c22-a9aa437e4a58'
    spike_rush = 'e921d1e6-416b-c31f-1291-74930c330b7b'
    snowball_fight = '57038d6d-49b1-3a74-c5ef-3395d9f23a97'
    practice = 'e2dc3878-4fe5-d132-28f8-3d8c259efcc6'
    on_board = 'd2b4e425-4cab-8d95-eb26-bb9b444551dc'
    swiftplay = '5d0f264b-4ebe-cc63-c147-809e1374484b'

    # aliases
    unrated = '96bd3920-4f36-d026-2b28-c683eb0bcac5'
    competitive = '96bd3920-4f36-d026-2b28-c683eb0bcac5'

    def __str__(self) -> str:
        return str(self.value)

    @property
    def url(self) -> str:
        return getattr(GameModeURL, self.name).value

    @classmethod
    def from_url(cls, game_mode_url: str) -> str:
        for x in cls:
            if x.url == game_mode_url:
                return str(x.value)
        raise ValueError(f'No game mode found for url {game_mode_url}')


class CurrencyType(Enum):
    valorant = '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'
    radianite = 'e59aa87c-4cbf-517a-5983-6e81511be9b7'
    free_agent = 'f08d4ae3-939c-4576-ab26-09ce1f23bb37'
    kingdom = '85ca954a-41f2-ce94-9b45-8ca3dd39a00d'

    # aliases
    vp = '85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741'
    rad = 'e59aa87c-4cbf-517a-5983-6e81511be9b7'

    def __str__(self) -> str:
        return str(self.value)


class SpraySlotID(Enum):
    slot_1 = '0814b2fe-4512-60a4-5288-1fbdcec6ca48'
    slot_2 = '04af080a-4071-487b-61c0-5b9c0cfaac74'
    slot_3 = '5863985e-43ac-b05d-cb2d-139e72970014'
    slot_4 = '7cdc908e-4f69-9140-a604-899bd879eed1'

    def __str__(self) -> str:
        return str(self.value)

    def __int__(self) -> int:
        return self.slot_number(self.value)

    @classmethod
    def slot_number(cls, slot_id: str) -> int:
        if slot_id == cls.slot_1.value:
            return 1
        elif slot_id == cls.slot_2.value:
            return 2
        elif slot_id == cls.slot_3.value:
            return 3
        elif slot_id == cls.slot_4.value:
            return 4

        raise ValueError(f'Unknown slot id: {slot_id}')


class SeasonType(Enum):
    episode = 'episode'
    act = 'act'


class LevelBorderID(Enum):
    empty = '00000000-0000-0000-0000-000000000000'
    _1 = 'ebc736cd-4b6a-137b-e2b0-1486e31312c9'
    _20 = '5156a90d-4d65-58d0-f6a8-48a0c003878a'
    _40 = '9c4afb15-40d7-3557-062a-4bb198cb9958'
    _60 = 'e6238102-425c-a647-6685-e6af7f8982d9'
    _80 = '49413ac2-4ed5-6953-5791-db838ccb58f3'
    _100 = 'e05371e3-4ec4-a53e-168a-c49346a75c19'
    _120 = '7e7feff1-44c2-301e-767d-d9b2b1cd9051'
    _140 = '53d4ed03-4b29-5913-aeda-80a41afcef3a'
    _160 = '6f610ab6-4a21-63fd-ac19-4a9204bc2721'
    _180 = '547ac9dd-495d-f11d-d921-3fbd14604ae0'
    _200 = 'bd1082ab-462c-3fb8-e049-28a9750acf0f'
    _220 = '37a36996-41f3-6e26-c00b-46bf7c037482'
    _240 = '5d0d6c6c-4f0a-dc65-e506-b786cc27dbe1'
    _260 = '3635b061-4bf9-b937-55fe-44a4dd0ed3dc'
    _280 = 'ae5eda0d-476b-a159-959c-df93374f4a69'
    _300 = '3d90bc3a-4626-71d6-a17c-93ae14d05fb0'
    _320 = '674bbd9e-4a4f-208a-75fa-1d9dd7d7008f'
    _340 = 'd84cf377-4c21-1cdf-0260-4e8ebd9825f5'
    _360 = '6c1fb61e-46e5-2908-5048-d4866cb64c3d'
    _380 = 'af1852a5-4e66-02a6-2ae3-ab8c885efb80'
    _400 = 'cbd1914e-43f8-7ae5-38c4-228bcbe58756'
    _420 = 'c8a4abff-4ace-f0a3-c9f3-db936791a697'
    _440 = '086dd1ab-4889-793a-4b33-0a99e311fa25'
    _460 = '08ab72f1-4fce-ddb5-5fd5-22abd3bc9d49'
    _480 = '6694d7f7-4ab9-8545-5921-35a9ea8cec24'

    def __str__(self) -> str:
        return str(self.value)


class BundleID(Enum):
    abyssal = 'afa6651a-4b93-b7f8-b136-b6b081fc3258'
    altitude = 'a4937ee9-4148-8ff2-2c11-c28891880306'
    araxys = 'a4c613c9-4970-61ca-e52a-918ae22f5315'
    arcane = '2270b116-4255-8a14-4486-db9de4979b89'
    avalanche = '0dee7ef6-d3ea-400a-b15c-5b9524243439'
    blastX = 'a31f7d1f-89d8-47ae-875b-1ae2117655c2'
    celestial = '473e694c-4940-078b-fb49-e994dff766cf'
    chrono_void = 'a5da7b5a-49a4-8fa9-a1c6-01a9aced0f9f'
    champions_2021 = 'bf987f36-4a33-45e4-3c49-1ab9a2502607'
    champions_2022 = 'f99e5b38-48c7-1146-acfa-9baaf773b844'
    cryostasis = '3ae56d5e-423d-97c5-1aa2-4faccccec1a2'
    crimson_beast = 'bd4f586d-469c-731d-5018-19835db2b086'
    doodle_buds = '2ed936df-4959-acc7-9aca-358d34a50619'
    ego = '2d6ec1d9-4152-8a43-5f7f-ff96b29c857f'
    elderflame = '1ba50cf0-46dd-848f-13a9-dc92fb0a3e3b'
    endeavour = '957f55ff-48a1-d0e2-41b1-ca89bf036b6e'
    forsaken = '1b98ee1c-4d9a-9e9d-0b36-f1a001a76628'
    gaias_vengeance = 'e10e00ae-4dcc-3c4a-16f7-7e885314f0d0'
    give_back_2021 = '441117e1-40be-42e2-3aeb-49957e5c03fd'
    give_back_2022 = '35a66d96-4c72-ea81-f09e-43a967b64c66'
    glitchpop = 'fc723fef-444a-4013-a741-3e85a97382f2'
    glitchpop_2 = '05e8add9-404d-5d37-8973-9f93f8880e2d'
    gravitational_uranium_neuroblaster = 'e84d5a16-462f-6fbf-bee0-5a80191a19e5'
    horizon = 'abba1438-4900-ce9b-8b81-38b6975a419f'
    infantry = '9be3549b-4124-7fc2-aa79-8d817f728a18'
    ion = '693d675e-4ed2-c00a-5e38-6b859b275565'
    ion_2 = '790f52c4-4ed8-9869-fa8b-bf92fc24b441'
    kuhaku_and_matsuba = '31827d9c-4ccb-8687-a5c1-69991ad1ec98'
    luna = 'ef488eb7-4405-3b3f-7fd1-63af0824a639'
    luxe = '1703b166-4e32-63da-9d16-a7a144aab574'
    magepunk = '338cabdb-473f-1f37-fa35-47a3d994517f'
    magepunk_2 = 'a981af4a-4d81-9668-8923-9c84c43da3d3'
    minima = 'cd095669-4a29-a7f3-e00d-f694186863cc'
    nebula = 'c520fbb0-492c-960e-8b77-f69fc4ce1838'
    neptune = 'ce15405a-4471-3290-1a16-abab355f97da'
    nunca_olvidados = 'a4d5c5f5-4647-d984-011d-dea2ef7b56c5'
    oni = 'ebfb909d-45ba-c514-3369-55bf014ba293'
    oni_2_0 = 'b7d754d4-44aa-4663-afc3-84a5cccc3c9d"'
    origin = '54f8793c-4daa-6e45-bcfd-e9bfc742dc30'
    prelude_to_chaos = '526f7d0c-414b-24bb-bcd0-10aed1f3e824'
    pride = '7b6b00f0-4fb9-7395-067d-44bcb4e20d9a'
    prime = '2116a38e-4b71-f169-0d16-ce9289af4bfa'
    prime_2_0 = 'de041dd5-4e17-2924-6d09-b4a3ccd82e6f'
    prism = 'ce6c1fa1-4eae-6db9-779f-f6988b866de4'
    prism_ii = '224ddcc4-4a2b-cc61-01a2-97835777b3f6'
    protocol781_A = 'ab83f73d-485f-e010-8ea0-24b538468a1a'
    RGX11z_pro = 'ed453815-44aa-4c4d-f3aa-77b4bcf048d7'
    RGX11z_pro_2 = 'd958b181-4e7b-dc60-7c3c-e3a3a376a8d2'
    radiant_crisis001 = '3a824027-4414-5a08-64f0-c8905a2aaa66'
    reaver = '81d85522-4651-4f66-72de-5fa057b3514c'
    reaver_2 = 'f7dcf7e1-485e-0524-ec82-0d97b2c8b40b'
    recon = 'b6b1b7ea-4a10-f810-a416-03adbb69d379'
    reverie = '9a4ad6ad-4aa9-695a-b73e-cf874223db0c'
    ruination = 'ae0c9cc4-4c03-f8d6-745c-84953db684fc'
    run_it_back = '332d705c-4852-11e5-c590-88b1f6e47f72'
    run_it_Back_2 = 'bcdd8956-4588-f586-fda8-fd991c593449'
    run_it_back_3 = 'a6fa35c6-4205-d5bc-dd65-3b92aeaac412'
    sarmad = '83e78a53-435b-f891-9e04-a9b59ed8fa44'
    sakura = '49d7951e-4e5d-304c-31a0-589b79096d5a'
    sensation = '54cbf45c-4b92-5cd9-07ab-3d98175fafa6'
    sentinels_of_light = '13d427c1-49d7-44f9-6576-27a9c83d787f'
    silvanus = '3aaeac8c-469f-bf29-7802-a09cc8729a3e'
    singularity = 'ef72e3c0-467b-ab15-076a-1e9690d16d6f'
    smite = 'adec612c-4c82-a4b2-a5f2-b7909e638a67'
    snowfall = '8a3507cd-44ef-0695-1d66-4da0f87e7522'
    sovereign = 'fd9fd08f-446f-018f-c632-0e96428f2978'
    soul_strife = 'bd94a6b3-4dfc-d333-8ba0-82a34d924ed7'
    spectrum = 'f7f37856-4af7-9b0e-08aa-91a5207c0439'
    spline = 'c1b255e2-411d-b159-6da3-5ab6c011a8cf'
    team_ace = 'f7bf90a6-4e39-6c04-c12a-b79c8842359c'
    tethered_realms = '1b632bcd-4e3d-eb8e-cca6-cebf937e6ebb'
    tigris = 'f1befd6b-4270-01b6-8a43-06b52fa417ae'
    titanmail = '866ce9c2-4493-daba-a025-7c805c4e3eed'
    undercity = 'd84cd2bf-42e5-34e8-062f-cba8d2c66fb2'
    valorant_go_vol_1 = 'b37b6a01-40f9-af81-ed34-fd8563539d44'
    valorant_go_vol_2 = '5c8b9297-465f-080c-3c0d-c9b9811432ed'
    wasteland = '4e3a244b-4482-0541-3eab-b8912cdb72d6'
    winterwunderland = '79d2f4b9-4066-8b5b-884f-1d95b33d2ac5'
    xenohunter = '3941ad01-4e3b-46e0-ba3a-ab94f7c67f98'
    vct_lock_in = '2654d506-4d05-e7e9-c996-63ac6fdaf767'

    def __str__(self) -> str:
        return str(self.value)


class RoundResultType(Enum):
    eliminated = 'Eliminated'
    bomb_defused = 'Bomb defused'
    bomb_detonated = 'Bomb detonated'
    timer_expired = 'Round timer expired'

    def __str__(self) -> str:
        return str(self.value)


class RoundResultCode(Enum):
    surrendered = 'Surrendered'
    elimination = 'Elimination'
    detonate = 'Detonate'
    defuse = 'Defuse'
    null = ''

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
