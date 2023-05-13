from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class History(TypedDict):
    MatchID: str
    GameStartTime: int
    QueueID: int


class MatchHistory(TypedDict):
    Subject: str
    BeginIndex: int
    EndIndex: int
    Total: int
    History: List[History]


class MatchInfo(TypedDict):
    matchId: str
    mapId: str
    gamePodId: str
    gameLoopZone: str
    gameServerAddress: str
    gameVersion: str
    gameLengthMillis: int
    gameStartMillis: int
    provisioningFlowID: str  # TODO: literal
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
    premierMatchInfo: Any  # TODO: add patch 06.08, implement
    partyRRPenalties: Dict[str, float]  # NOTE: int or float?
    shouldMatchDisablePenalties: bool


class PlatformInfo(TypedDict):
    platformType: str  # Literal['PC'] # NOTE: add other platforms ?
    platformOS: str  # Literal['Windows'] # NOTE: add other platforms ?
    platformOSVersion: str
    platformChipset: str


class AbilityCasts(TypedDict):
    grenadeCasts: int
    ability1Casts: int
    ability2Casts: int
    ultimateCasts: int


class PlayerStats(TypedDict):
    score: int
    roundsPlayed: int
    kills: int
    deaths: int
    assists: int
    playtimeMillis: int
    abilityCasts: AbilityCasts


# fmt: off
RoundDamage = TypedDict(
    'RoundDamage', {
        'round': int,
        'receiver': str,
        'damage': int}
)
# fmt: on


class BehaviorFactors(TypedDict):
    afkRounds: int
    collisions: float
    damageParticipationOutgoing: int
    friendlyFireIncoming: int
    friendlyFireOutgoing: int
    mouseMovement: int
    stayedInSpawnRounds: int


class XPModification(TypedDict):
    Value: float
    ID: str


class NewPlayerExperience(TypedDict):
    idleTimeMillis: int
    objectiveCompleteTimeMillis: int


class BasicMovement(NewPlayerExperience):
    pass


class BasicGunSkill(NewPlayerExperience):
    pass


class AdaptiveBots(NewPlayerExperience):
    adaptiveBotAverageDurationMillisAllAttempts: int
    adaptiveBotAverageDurationMillisFirstAttempt: int
    killDetailsFirstAttempt: Optional[Any]


class Ability(NewPlayerExperience):
    pass


class BombPlant(NewPlayerExperience):
    pass


class DefendBombSite(NewPlayerExperience):
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


class Player(TypedDict):
    subject: str
    gameName: str
    tagLine: str
    platformInfo: PlatformInfo
    teamId: str  # Literal['Blue', 'Red']
    partyId: str
    characterId: str
    stats: PlayerStats
    roundDamage: List[RoundDamage]
    competitiveTier: int
    isObserver: bool
    playerCard: str
    playerTitle: str
    preferredLevelBorder: str
    accountLevel: int
    sessionPlaytimeMinutes: int
    xpModifications: NotRequired[List[XPModification]]
    behaviorFactors: BehaviorFactors
    newPlayerExperienceDetails: NewPlayerExperienceDetails


class Coach(TypedDict):
    subject: str
    teamId: str


class Team(TypedDict):
    teamId: Literal['Red', 'Blue']
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


class RoundPlayerStatKill(TypedDict):
    gameTime: int
    roundTime: int
    killer: str
    victim: str
    victimLocation: Location
    assistants: List[str]
    playerLocations: Optional[List[PlayerLocation]]
    finishingDamage: FinishingDamage


class RoundPlayerDamage(TypedDict):
    receiver: str
    damage: int
    legshots: int
    bodyshots: int
    headshots: int


class Economy(TypedDict):
    loadoutValue: int
    weapon: str
    armor: str
    remaining: int
    spent: int


class RoundPlayerAbility(TypedDict):
    grenadeEffects: Optional[Any]
    ability1Effects: Optional[Any]
    ability2Effects: Optional[Any]
    ultimateEffects: Optional[Any]


class RoundPlayerStats(TypedDict):
    subject: str
    kills: List[RoundPlayerStatKill]
    damage: List[RoundPlayerDamage]
    score: int
    economy: Economy
    ability: RoundPlayerAbility
    wasAfk: bool
    wasPenalized: bool
    stayedInSpawn: bool


class RoundPlayerEconomy(Economy):
    subject: str
    loadoutValue: int
    weapon: str
    armor: str
    remaining: int
    spent: int


class RoundPlayerScore(TypedDict):
    subject: str
    score: int


class RoundResult(TypedDict):
    roundNum: int
    roundResult: str  # TODO: Literal
    roundCeremony: str
    winningTeam: Literal['Red', 'Blue']
    bombPlanter: NotRequired[str]
    bombDefuser: NotRequired[str]
    plantRoundTime: int
    plantPlayerLocations: Optional[List[PlayerLocation]]
    plantLocation: Location
    plantSite: Literal['A', 'B', 'C']
    defuseRoundTime: int
    defusePlayerLocations: Optional[List[PlayerLocation]]
    defuseLocation: Location
    playerStats: List[RoundPlayerStats]
    roundResultCode: str  # TODO: Literal
    playerEconomies: List[RoundPlayerEconomy]
    playerScores: List[RoundPlayerScore]


Kill = TypedDict(
    'MatchKill',
    {
        'gameTime': int,
        'roundTime': int,
        'round': int,
        'killer': str,
        'victim': str,
        'victimLocation': Location,
        'assistants': List[str],
        'playerLocations': List[PlayerLocation],
        'finishingDamage': FinishingDamage,
    },
)


class MatchDetails(TypedDict):
    matchInfo: MatchInfo
    players: List[Player]
    bots: List[Any]  # NOTE: unknown type
    coaches: List[Coach]
    teams: List[Team]
    roundResults: List[RoundResult]
    kills: List[Kill]
