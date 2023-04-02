from typing import Dict, List, Optional, TypedDict, Union

from .response import Response


class Role(TypedDict):
    uuid: str
    displayName: Union[str, Dict[str, str]]
    description: Union[str, Dict[str, str]]
    displayIcon: str
    assetPath: str


class Ability(TypedDict):
    slot: str
    displayName: Union[str, Dict[str, str]]
    description: Union[str, Dict[str, str]]
    displayIcon: str


class Media(TypedDict):
    id: int
    wwise: str
    wave: str


class VoiceLine(TypedDict):
    minDuration: float
    maxDuration: float
    mediaList: List[Media]


class Agent(TypedDict):
    uuid: str
    displayName: Union[str, Dict[str, str]]
    description: Union[str, Dict[str, str]]
    developerName: str
    characterTags: List[Union[str, Dict[str, str]]]
    displayIcon: str
    displayIconSmall: str
    bustPortrait: str
    fullPortrait: str
    fullPortraitV2: str
    killfeedPortrait: str
    background: str
    backgroundGradientColors: List[str]
    assetPath: str
    isFullPortraitRightFacing: bool
    isPlayableCharacter: bool
    isAvailableForTest: bool
    isBaseContent: bool
    role: Role
    abilities: List[Ability]
    voiceLine: VoiceLine


Data = Response[Agent]
