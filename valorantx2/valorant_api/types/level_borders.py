from .object import Object
from .response import Response


class LevelBorder(Object):
    startingLevel: int
    levelNumberAppearance: str
    smallPlayerCardAppearance: str
    assetPath: str


LevelBorders = Response[LevelBorder]
