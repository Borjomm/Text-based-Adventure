import globals as g
from typing import Callable

def wrap_key(loc_key: str) -> Callable:
    return lambda key=loc_key: g.loc.translate(key)