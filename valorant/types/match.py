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

from typing_extensions import NotRequired

from .player import Player


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
    forcePostProcessing: bool
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


class AbilityCasts(TypedDict):
    grenadeCasts: int
    ability1Casts: int
    ability2Casts: int
    ultimateCasts: int


class AbilityEffect(TypedDict):
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
    abilityCasts: AbilityCasts


class XpModification(TypedDict):
    Value: float
    ID: str


class BasicNewPlayer(TypedDict):
    idleTimeMillis: int
    objectiveCompleteTimeMillis: int


class BasicMovement(BasicNewPlayer):
    pass


class BasicGunSkill(BasicNewPlayer):
    pass


class AdaptiveBots(BasicNewPlayer):
    adaptiveBotAverageDurationMillisAllAttempts: int
    adaptiveBotAverageDurationMillisFirstAttempt: int
    killDetailsFirstAttempt: Optional[Any]


class Ability(BasicNewPlayer):
    pass


class BombPlant(BasicNewPlayer):
    pass


class DefendBombSite(BasicNewPlayer):
    success: bool


class SettingStatus(TypedDict):
    isMouseSensitivityDefault: bool
    isCrosshairDefault: bool


class NewPlayerExperienceDetails:
    basicMovement: BasicMovement
    basicGunSkill: BasicGunSkill
    adaptiveBots: AdaptiveBots
    ability: Ability
    bombPlant: BombPlant
    defendBombSite: DefendBombSite
    settingStatus: SettingStatus


class BehaviorFactors(TypedDict):
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


class PlayerLocation(TypedDict):
    subject: str
    viewRadians: float
    location: Location


class FinishingDamage(TypedDict):
    damageType: str
    damageItem: str
    isSecondaryFireMode: bool


class MatchKill(TypedDict):
    gameTime: int
    roundTime: int
    round: int
    killer: str
    victim: str
    victimLocation: Location
    assistants: List[str]
    playerLocations: List[PlayerLocation]
    finishingDamage: FinishingDamage


class Economy(TypedDict):
    loadoutValue: int
    weapon: str
    armor: str
    remaining: int
    spent: int


class PlayerEconomy(Economy):
    subject: str


class PlayerScore(TypedDict):
    subject: str
    score: int


class PlayerStatKill(TypedDict):
    gameTime: int
    roundTime: int
    killer: str
    victim: str
    victimLocation: Location
    assistants: List[str]
    playerLocations: Optional[List[PlayerLocation]]
    finishingDamage: FinishingDamage


class PlayerDamage(TypedDict):
    receiver: str
    damage: int
    legshots: int
    bodyshots: int
    headshots: int


class MatchRoundPlayerStats(TypedDict):
    subject: str
    kills: List[PlayerStatKill]
    damage: List[PlayerDamage]
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
    bombPlanter: NotRequired[str]
    bombDefuser: NotRequired[str]
    plantRoundTime: int
    plantPlayerLocations: Optional[List[PlayerLocation]]
    plantLocation: Location
    plantSite: str
    defuseRoundTime: int
    defusePlayerLocations: Optional[List[PlayerLocation]]
    defuseLocation: Location
    playerStats: List[MatchRoundPlayerStats]
    roundResultCode: str
    playerEconomies: List[PlayerEconomy]
    playerScores: List[PlayerScore]


class Coach(TypedDict):
    subject: str
    teamId: str


class MatchDetails(TypedDict):
    matchInfo: MatchInfo
    players: List[PlayerMatch]
    bots: List[Dict[str, Any]]  # TODO: i dont know what this is
    coaches: List[Coach]
    teams: List[Team]
    roundResults: List[MatchRoundResult]
    kills: List[MatchKill]


class PlayerMatch(Player):
    subject: str
    gameName: str
    tagLine: str
    platformInfo: MatchPlayerPlatformInfo
    teamId: str
    partyId: str
    characterId: str
    stats: MatchPlayerStats
    roundDamage: List[RoundDamage]
    competitiveTier: int
    playerCard: str
    playerTitle: str
    preferredLevelBorder: str
    accountLevel: int
    sessionPlaytimeMinutes: int
    xpModifications: List[XpModification]
    behaviorFactors: BehaviorFactors
    newPlayerExperienceDetails: NewPlayerExperienceDetails
