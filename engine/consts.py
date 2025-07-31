from enum import Enum, auto

class BattleResult(Enum):
    VICTORY = auto()
    DEFEAT = auto()

class Keybinds(Enum):
    QUIT = 'q'
    ARR_UP = 'up'
    ARR_DOWN = 'down'
    ARR_RIGHT = 'right'
    ARR_LEFT = 'left'
    ENTER = 'c-m'
    LOGKEY = 'l'
    YESKEY = 'y'
    NOKEY = 'n'

class DataPaths(Enum):
    DATA_FOLDER = "data"
    ENEMIES = "enemies.yaml"
    PLAYER_CLASSES = "player_classes.yaml"