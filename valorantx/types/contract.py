"""
The MIT License (MIT)

Copyright (c) 2022-present xStacia

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union


class ContractProgression(TypedDict):
    TotalProgressionEarned: int
    HighestRewardedLevel: Dict[str, int]  # I don't know what this is


class Contract(TypedDict):
    ContractDefinitionID: str
    ContractProgression: ContractProgression
    ProgressionLevelReached: int
    ProgressionTowardsNextLevel: int


class ProcessedMatch(TypedDict):
    ID: str
    StartTime: Union[datetime, int]
    XPGrants: Optional[Any]
    RewardGrants: Optional[Any]
    MissionDeltas: Optional[Any]
    ContractDeltas: Optional[Any]
    CouldProgressMissions: bool


class Mission(TypedDict):
    ID: str
    Objectives: Dict[str, int]
    Complete: bool
    ExpirationTime: Union[datetime, str]


class MissionMeta(TypedDict):
    NPECompleted: bool
    WeeklyCheckpoint: Union[datetime, str]
    WeeklyRefillTime: Union[datetime, str]


class Contracts(TypedDict):
    Version: int
    Subject: str
    Contracts: List[Contract]
    ProcessedMatches: List[ProcessedMatch]
    ActiveSpecialContract: str
    Missions: List[Mission]
    MissionMetadata: MissionMeta
