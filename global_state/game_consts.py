from enum import Enum, auto

class Defaults(Enum):
    ATTACK_OFFSET = 2
    ENEMY_ID = 100
    PLAYER_HEAL_VALUE = 20
    ACTION_VALUE_SCALE = 10000

class PlayerClass(Enum):
    WARRIOR = auto()
    THIEF = auto()
    MAGE = auto()

class EntityType(Enum):
    PLAYER = auto()
    ENEMY = auto()

class ActionTypes(Enum):
    TARGETED = auto()
    NON_TARGETED = auto()

class Actions(Enum):
    HEAL = ActionTypes.NON_TARGETED
    ATTACK = ActionTypes.TARGETED
    

class BattleResult(Enum):
    VICTORY = auto()
    DEFEAT = auto()

class Scope(Enum):
    SELF = auto()
    ALLIES = auto()
    ENEMIES = auto()

class Proportionality(Enum):
    DIRECT = auto()
    INVERSE = auto()

class Stats(Enum):
    ATTACK = auto()
    SPEED = auto()