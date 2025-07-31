from global_state.consts import LANGUAGES

from ..option_classes import ConfigOption

MAIN_CONFIG_DICT = {
    "tick_speed": ConfigOption(
        default=20,
        type=int,
        validator=lambda v: max(1, min(v, 100)) # Clamps between 1 and 100
    ),
    "refresh_rate": ConfigOption(
        default=30.0,
        type=float,
        validator=lambda v: max(10.0, min(v, 60.0)) # Clamps between 10 and 60
    ),
    "language": ConfigOption(
        default="en",
        type=str,
        validator=lambda v: v if v in LANGUAGES else "en" # Ensures language is valid
    )
}