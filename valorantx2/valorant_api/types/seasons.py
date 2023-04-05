from typing import Dict, List, Union

from .object import Object
from .response import Response


class Season(Object):
    displayName: Union[str, Dict[str, str]]
    type: str
    startTime: str
    endTime: str
    parentUuid: str
    assetPath: str


Seasons = Response[List[Season]]
SeasonUUID = Response[Season]


class Border(Object):
    level: int
    winsRequired: int
    displayIcon: str
    smallIcon: str
    assetPath: str


class CompetitiveSeason(Object):
    startTime: str
    endTime: str
    seasonUuid: str
    competitiveTiersUuid: str
    borders: List[Border]
    assetPath: str


CompetitiveSeasons = Response[List[CompetitiveSeason]]
CompetitiveSeasonUUID = Response[CompetitiveSeason]
