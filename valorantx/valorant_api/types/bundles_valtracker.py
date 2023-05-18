from typing import List, Optional

from .object import Object
from .response import Response


class BuddyLevel(Object):
    displayIcon: str


class Buddy(Object):
    displayIcon: str
    levels: List[BuddyLevel]
    name: str
    price: Optional[int]


class PlayerCard(Object):
    displayIcon: str
    largeArt: str
    name: str
    price: Optional[int]
    smallArt: str
    wideArt: str


class Spray(Object):
    animatedGif: Optional[str]
    animatedPng: Optional[str]
    displayIcon: str
    name: str
    price: Optional[int]


class WeaponChroma(Object):
    displayIcon: Optional[str]
    fullRender: str
    name: str
    swatch: Optional[str]
    video: Optional[str]


class WeaponLevel(Object):
    displayIcon: Optional[str]
    levelType: Optional[str]  # not sure
    name: Optional[str]
    video: Optional[str]


class ContentTier(Object):
    displayIcon: str
    name: str


class Weapon(Object):
    chromas: List[WeaponChroma]
    contenttier: List[ContentTier]
    displayIcon: str
    levels: List[WeaponLevel]
    name: str
    price: Optional[int]


class Bundle(Object):
    buddies: List[Buddy]
    cards: List[PlayerCard]
    description: Optional[str]
    displayIcon: str
    displayIcon2: str
    last_seen: int
    name: str
    price: int
    promoDescription: Optional[str]
    sprays: List[Spray]
    useAdditionalContext: bool
    verticalPromoImage: str
    weapons: List[Weapon]


BundlesValTracker = Response[List[Bundle]]
