from abc import ABC, abstractmethod
from typing import Self, Optional, List

from engine.world import World


from engine.actions.ai_containers import Consideration
from global_state.game_consts import Scope
from events.event_containers import AbilityContainer
from events.events import Event

class AbstractAbility(ABC):
    @abstractmethod
    def __init__(self, id, arg_dict: dict):
        """MUST IMPLEMENT:
        ID, AP, SCOPE, KEY, TOOLTIP_KEY, DATA_DICT
        """

        self.id: int = id
        self.scope: Scope = Scope.ENEMIES
        self.ap: int = 1
        self.considerations: List[Optional[Consideration]] = []
        self.key: str = "abilities.null"
        self.tooltip_key: str = "abilities_tooltip.null"
        self.data_dict: dict = {}

    @abstractmethod
    def to_dict(self) -> dict:
        return {
            "id": self.id
        }
    
    @classmethod
    def from_dict(cls, arg_dict: dict) -> Self:
        ability_id = arg_dict["id"]
        return cls(ability_id, arg_dict)

    @classmethod
    @abstractmethod
    def check_args(cls, arg_dict: dict) -> bool:
        raise NotImplementedError(f"Method 'check_args' is not implemented in class {cls.__name__}")

    def evaluate(self, world: World, entity_id: int, enemy_set: set) -> tuple[Optional[int], float]:
        target_scores = {}

        all_target_factors = {}
        for target_id in enemy_set:
            if not self._is_available(world, entity_id, target_id):
                continue

            all_target_factors[target_id] = {}

            for consideration in self.considerations:
                score = consideration.func(world, entity_id, target_id, consideration.proportionality, **consideration.kwargs)
                all_target_factors[target_id][consideration.func] = score

        for consideration in self.considerations:
            if consideration.needs_normalization:
                raw_scores = [factors[consideration.func] for factors in all_target_factors.values()]
                max_score = max(raw_scores) if raw_scores else 0

                for target_id in all_target_factors:

                    if max_score > 0:
                        all_target_factors[target_id][consideration.func] /= max_score
                    else:
                        all_target_factors[target_id][consideration.func] = 0

        for target_id, factors in all_target_factors.items():
            final_score = 0
            for consideration in self.considerations:
                final_score += factors[consideration.func] * consideration.weight
            target_scores[target_id] = final_score

        if not target_scores:
            return (None, 0.0)
        
        best_target_id = max(target_scores, key=target_scores.get)
        best_score = target_scores[best_target_id]

        return (best_target_id, min(best_score, getattr(self, 'max_weight', 1.0)))
    
    @abstractmethod
    def execute(self, world: World, entity_id: int, target_id: Optional[int]) -> list[Event]:
        raise NotImplementedError(f"Method 'execute' is not implemented in class {self.__class__.__name__}")
    
    def get_state_package(self, world: World, entity_id: int) -> AbilityContainer:
        return AbilityContainer(self.id, self.ap, self.scope, self.key, self.tooltip_key, self.data_dict, self._is_available(world, entity_id))
    
    @abstractmethod
    def _is_available(self, world: World, entity_id: int, target_id: Optional[int] = None) -> bool:
        raise NotImplementedError(f"Method '_is_available' is not implemented in class {self.__class__.__name__}")
    
    
    
    
