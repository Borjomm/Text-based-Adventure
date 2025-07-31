from ..option_classes import KeyOption

KEY_CONFIG_DICT = {
    "log_key": KeyOption("l"),
    "quit_key": KeyOption("q"),
    "yes_key": KeyOption("y"),
    "no_key": KeyOption("n"),
    "arr_up": KeyOption("up", True),
    "arr_down": KeyOption("down", True),
    "arr_left": KeyOption("left", True),
    "arr_right": KeyOption("right", True),
    "enter_key": KeyOption("c-m", True),
    "tab_key": KeyOption("c-i", True)
}

BANNED_KEYBINDS = {
    "escape"
}