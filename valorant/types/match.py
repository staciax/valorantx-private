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
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from .player import PlayerMatch


class MatchHistoryList(TypedDict):
    MatchID: str
    GameStartTime: int
    QueueID: int


class MatchHistory(TypedDict):
    Subject: str
    BeginIndex: int
    EndIndex: int
    Total: int
    History: List[MatchHistoryList]


class MatchInfo(TypedDict):
    matchId: str
    mapId: str
    gamePodId: str
    gameLoopZone: str
    gameServerAddress: str
    gameVersion: str
    gameLengthMillis: int
    gameStartMillis: int
    provisioningFlowID: str
    isCompleted: bool
    customGameName: str
    forcePostProcessing: str
    queueID: str
    gameMode: str
    isRanked: bool
    isMatchSampled: bool
    seasonId: str
    completionState: str
    platformType: str
    partyRRPenalties: Dict[str, float]
    shouldMatchDisablePenalties: bool


class MatchPlayerPlatformInfo(TypedDict):
    platformType: str
    platformOS: str
    platformOSVersion: str
    platformChipset: str


class RoundDamage(TypedDict):
    round: int
    receiver: str
    damage: int


class abilityCasts(TypedDict):
    grenadeCasts: int
    ability1Casts: int
    ability2Casts: int
    ultimateCasts: int


class abilityEffect(TypedDict):
    ability1Effect: Optional[Any]
    ability2Effect: Optional[Any]
    ultimateEffect: Optional[Any]


class MatchPlayerStats(TypedDict):
    score: int
    roundsPlayed: int
    kills: int
    deaths: int
    assists: int
    playtimeMillis: int
    abilityCasts: abilityCasts


class xpModification(TypedDict):
    Value: float
    ID: str


class basicNewPlayer(TypedDict):
    idleTimeMillis: int
    objectiveCompleteTimeMillis: int


class basicMovement(basicNewPlayer):
    pass


class basicGunSkill(basicNewPlayer):
    pass


class adaptiveBots(basicNewPlayer):
    adaptiveBotAverageDurationMillisAllAttempts: int
    adaptiveBotAverageDurationMillisFirstAttempt: int
    killDetailsFirstAttempt: Optional[Any]


class ability(basicNewPlayer):
    pass


class bombPlant(basicNewPlayer):
    pass


class defendBombSite(basicNewPlayer):
    success: bool


class settingStatus(TypedDict):
    isMouseSensitivityDefault: bool
    isCrosshairDefault: bool


class newPlayerExperienceDetails:
    basicMovement: basicMovement
    basicGunSkill: basicGunSkill
    adaptiveBots: adaptiveBots
    ability: ability
    bombPlant: bombPlant
    defendBombSite: defendBombSite
    settingStatus: settingStatus


class behaviorFactors(TypedDict):
    afkRounds: int
    collisions: float
    damageParticipationOutgoing: int
    friendlyFireIncoming: int
    friendlyFireOutgoing: int
    mouseMovement: int
    stayedInSpawnRounds: int


class Team(TypedDict):
    teamId: str
    won: bool
    roundsPlayed: int
    roundsWon: int
    numPoints: int


class Location(TypedDict):
    x: int
    y: int


class playerLocation(TypedDict):
    subject: str
    viewRadians: float
    location: Location


class finishingDamage(TypedDict):
    damageType: str
    damageItem: str
    isSecondaryFireMode: bool


class MatchKill(TypedDict):
    gameTime: str
    roundTime: str
    round: int
    killer: str
    victim: str
    victimLocation: Location
    assistants: List[str]
    playerLocations: List[playerLocation]
    finishingDamage: finishingDamage


class Economy(TypedDict):
    loadoutValue: int
    weapon: str
    armor: str
    remaining: int
    spent: int


class playerEconomy(Economy):
    subject: str


class playerScore(TypedDict):
    subject: str
    score: int


class playerStatKill(TypedDict):
    gameTime: int
    roundTime: int
    killer: str
    victim: str
    victimLocation: Location
    assistants: List[str]
    playerLocations: playerLocation
    finishingDamage: finishingDamage


class playerDamage(TypedDict):
    receiver: str
    damage: int
    legshots: int
    bodyshots: int
    headshots: int


class MatchRoundPlayerStats(TypedDict):
    subject: str
    kills: List[playerStatKill]
    damage: List[playerDamage]
    score: int
    economy: Economy
    ability: Dict[Any, Any]
    wasAfk: bool
    wasPenalized: bool
    stayedInSpawn: bool


class MatchRoundResult(TypedDict, total=False):
    roundNum: int
    roundResult: str
    roundCeremony: str
    winningTeam: str
    plantRoundTime: int
    plantPlayerLocations: Optional[Any]
    plantLocation: Location
    plantSite: str
    defuseRoundTime: int
    defusePlayerLocations: Optional[List[playerLocation]]
    defuseLocation: Location
    playerStats: List[MatchRoundPlayerStats]
    roundResultCode: str
    playerEconomies: List[playerEconomy]
    playerScores: List[playerScore]


class MatchDetails(TypedDict):
    matchInfo: MatchInfo
    players: List[PlayerMatch]
    bots: List[Dict[str, Any]]  # TODO: i dont know what this is
    coaches: List[Dict[str, Any]]  # TODO: i dont know what this is
    teams: List[Team]
    roundResults: List[MatchRoundResult]
    kills: List[MatchKill]
