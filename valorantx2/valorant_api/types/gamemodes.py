from typing import Dict, List, Optional, Union

from .object import Object
from .response import Response


class GameFeatureOverride(Object):
    featureName: str
    state: bool


class GameRuleBoolOverride(Object):
    ruleName: str
    state: bool


class GameMode(Object):
    displayName: Union[str, Dict[str, str]]
    duration: Union[str, Dict[str, str]]
    allowsMatchTimeouts: bool
    isTeamVoiceAllowed: bool
    isMinimapHidden: bool
    orbCount: int
    roundsPerHalf: int
    teamRoles: Optional[List[str]]
    gameFeatureOverrides: Optional[List[GameFeatureOverride]]
    gameRuleBoolOverrides: Optional[List[GameRuleBoolOverride]]
    displayIcon: Optional[str]
    assetPath: str


GameModes = Response[GameMode]


class GameModeEquippable(Object):
    displayName: Union[str, Dict[str, str]]
    category: str
    displayIcon: str
    killStreamIcon: str
    assetPath: str


GameModeEquippables = Response[GameModeEquippable]
