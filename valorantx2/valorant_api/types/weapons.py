from typing import Dict, List, Optional, TypedDict, Union

from .object import Object
from .response import Response


class AdsStats(TypedDict):
    zoomMultiplier: float
    fireRate: float
    runSpeedMultiplier: float
    burstCount: int
    firstBulletAccuracy: float


class AltShotgunStats(TypedDict):
    shotgunPelletCount: int
    burstRate: float


class AirBurstStats(TypedDict):
    shotgunPelletCount: int
    burstDistance: float


class DamageRange(TypedDict):
    rangeStartMeters: float
    rangeEndMeters: float
    headDamage: float
    bodyDamage: float
    legDamage: float


class WeaponStats(TypedDict):
    fireRate: float
    magazineSize: int
    runSpeedMultiplier: float
    equipTimeSeconds: float
    reloadTimeSeconds: float
    firstBulletAccuracy: float
    shotgunPelletCount: int
    wallPenetration: str
    feature: Optional[str]
    fireMode: Optional[str]
    altFireType: Optional[str]
    adsStats: Optional[AdsStats]
    altShotgunStats: Optional[AltShotgunStats]
    airBurstStats: Optional[AirBurstStats]
    damageRanges: List[DamageRange]


class GridPosition(TypedDict):
    row: int
    column: int


class ShopData(TypedDict):
    cost: int
    category: str
    categoryText: Union[str, Dict[str, str]]
    gridPosition: GridPosition
    canBeTrashed: bool
    image: str
    newImage: str
    newImage2: str
    assetPath: str


class Chroma(Object):
    displayName: Union[str, Dict[str, str]]
    displayIcon: Optional[str]
    fullRender: str
    swatch: Optional[str]
    streamedVideo: Optional[str]
    assetPath: str


class Level(Object):
    displayName: Union[str, Dict[str, str]]
    levelItem: str
    displayIcon: Optional[str]
    streamedVideo: Optional[str]
    assetPath: str


class Skin(Object):
    displayName: Union[str, Dict[str, str]]
    themeUuid: str
    contentTierUuid: str
    displayIcon: str
    wallpaper: str
    assetPath: str
    chromas: List[Chroma]
    levels: List[Level]


class Weapon(Object):
    displayName: Union[str, Dict[str, str]]
    category: str
    defaultSkinUuid: str
    displayIcon: str
    killStreamIcon: str
    assetPath: str
    weaponStats: Optional[WeaponStats]
    shopData: Optional[ShopData]
    skins: List[Skin]


Weapons = Response[List[Weapon]]
WeaponUUID = Response[Weapon]

Skins = Response[List[Skin]]
SkinUUID = Response[Skin]

SkinLevels = Response[List[Level]]
SkinLevel = Level
SkinLevelUUID = Response[Level]

SkinChromas = Response[List[Chroma]]
SkinChroma = Chroma
SkinChromaUUID = Response[Chroma]
