from typing import Dict, List, Union

from .object import Object
from .response import Response


class Gamemode(Object):
    displayName: Union[str, Dict[str, str]]
    category: str
    displayIcon: str
    killStreamIcon: str
    assetPath: str


Gamemodes = Response[Gamemode]


class GameFeatureOverride(Object):
    featureName: str
    state: bool


class GameRuleBoolOverride(Object):
    ruleName: str
    state: bool


class GamemodeEquippable(Object):
    displayName: Union[str, Dict[str, str]]
    duration: Union[int, Dict[str, int]]
    allowsMatchTimeouts: bool
    isTeamVoiceAllowed: bool
    isMinimapHidden: bool
    orbCount: int
    roundsPerHalf: int
    teamRoles: List[str]
    gameFeatureOverrides: List[GameFeatureOverride]
    gameRuleBoolOverrides: List[GameRuleBoolOverride]
    displayIcon: str
    assetPath: str


GamemodeEquippables = Response[GamemodeEquippable]
