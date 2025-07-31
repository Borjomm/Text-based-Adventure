from global_state.consts import UNIQUE_ABILITY_MAP, BASIC_ABILITY_MAP

def register_ability(name: str, unique: bool):
    def decorator(cls):
        if unique:
            UNIQUE_ABILITY_MAP[name] = cls
        else:
            BASIC_ABILITY_MAP[name] = cls
        return cls
    return decorator