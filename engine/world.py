from typing import Set, Dict, Any, Type, Tuple, List
from collections import defaultdict

# Define generic types for clarity.
# In a real ECS, your components would be actual classes (e.g., dataclasses).
# Example:
# @dataclass
# class Position:
#     x: int
#     y: int
#
# So ComponentType would be 'Position' (the class itself)
# and ComponentData would be 'Position(x=10, y=20)' (an instance of the class)

ComponentType = Type[Any]  # Represents the component class (e.g., Position)
ComponentData = Any        # Represents an instance of a component (e.g., Position(x=10, y=20))

class World:
    """
    A basic Entity-Component-System (ECS) World implementation.
    Manages entities, components, and provides querying capabilities.
    """
    def __init__(self):
        # Stores components: _world[ComponentType][entity_id] = ComponentData
        # Using defaultdict ensures that _world[ComponentType] always returns a dict
        self._world: Dict[ComponentType, Dict[int, ComponentData]] = defaultdict(dict)
        # Stores all active entity IDs
        self._entities: Set[int] = set()
        # Next available entity ID for creation
        self._next_id: int = 0

    def get_all_entities(self) -> Set[int]:
        return set(self._entities)
    
    def has_component(self, entity_id: int, *component_type: ComponentType) -> bool:
        for component in component_type:
            if not entity_id in self._world.get(component, {}):
                return False
        return True

    def create_entity(self) -> int:
        """
        Creates a new unique entity ID and adds it to the world.
        Returns the new entity ID.
        """
        eid = self._next_id
        self._next_id += 1
        self._entities.add(eid)
        return eid
    
    def _entity_exists(self, entity_id: int) -> None:
        """
        Internal helper to check if an entity exists.
        Raises ValueError if the entity_id is not found.
        """
        if entity_id not in self._entities:
            raise ValueError(f"Entity {entity_id} does not exist in the world.")

    def add_component(self, entity_id: int, component_data: ComponentData):
        """
        Adds a component instance to a specific entity.
        The component's class (type) is used as the key for storage.
        
        Args:
            entity_id: The ID of the entity to add the component to.
            component_data: An instance of a component class (e.g., Position(x=10, y=20)).
        """
        self._entity_exists(entity_id)
        
        component_type = type(component_data) # Get the class of the component instance
        
        # Add/update the component data for the entity.
        # defaultdict handles the creation of _world[component_type] if it doesn't exist.
        self._world[component_type][entity_id] = component_data

    def add_components(self, entity_id: int, *components_data: ComponentData):
        """
        The same as 'add_component', but with multiple components to be added at once
        """
        for component in components_data:
            self.add_component(entity_id, component)

    def get_component(self, entity_id: int, component_type: ComponentType) -> ComponentData | None:
        """
        Retrieves a component instance for a given entity and component type.
        
        Args:
            entity_id: The ID of the entity.
            component_type: The class of the component to retrieve (e.g., Position).
            
        Returns:
            The component instance if found, otherwise None.
        """
        self._entity_exists(entity_id)
        
        # Safely get the dictionary for the component type, then safely get the component for the entity
        # Using .get() on _world[component_type] is safe because defaultdict ensures _world[component_type] exists
        return self._world[component_type].get(entity_id)

    def remove_component(self, entity_id: int, component_type: ComponentType):
        """
        Removes a component of a specific type from an entity.
        
        Args:
            entity_id: The ID of the entity.
            component_type: The class of the component to remove (e.g., Position).
        """
        self._entity_exists(entity_id)
        
        # Check if the entity actually has this component
        if entity_id in self._world[component_type]: # defaultdict ensures _world[component_type] exists
            del self._world[component_type][entity_id]
            # Clean up: if the component type's dictionary becomes empty, remove it from _world
            if not self._world[component_type]:
                del self._world[component_type] # Remove the empty defaultdict entry
        # Else: the component wasn't there, do nothing. No error needed as per typical remove behavior.

    def get_entities_with(self, *component_types: ComponentType) -> Set[int]:
        """
        Returns a set of entity IDs that possess all specified component types.
        
        Args:
            *component_types: One or more component classes (e.g., Position, Velocity).
            
        Returns:
            A set of entity IDs matching the query. An empty set if no entities match.
        """
        if not component_types:
            return set() # No components requested, return empty set
        
        # New approach:
        # 1. First, check if all requested component types exist in the world's _world map
        #    AND if they have any entities associated with them.
        #    If even one requested component type has NO entities associated with it,
        #    then the intersection will inevitably be empty.
        
        # Collect component types and their entity sets
        component_entity_sets: List[Tuple[ComponentType, Set[int]]] = []
        for ct in component_types:
            # _world[ct] will return the dict for that component type (empty if no entities have it)
            entity_ids_for_ct = self._world[ct].keys() 
            
            # If a required component type has no entities, the intersection is immediately empty.
            if not entity_ids_for_ct:
                return set() 
            
            component_entity_sets.append((ct, set(entity_ids_for_ct))) # Convert keys to set once

        # Optimization: Sort the collected sets by size (smallest first)
        component_entity_sets.sort(key=lambda x: len(x[1]))
        
        # Initialize the intersection set with the smallest set of entities
        initial_set = component_entity_sets[0][1]

        # Perform intersection with remaining component sets
        for _, current_set in component_entity_sets[1:]:
            initial_set.intersection_update(current_set)
            
            # Early exit if the intersection becomes empty at any point
            if not initial_set:
                return set() 

        return initial_set
        
    def get_components_of(self, entity_id: int) -> Dict[ComponentType, ComponentData]:
        """
        Returns a dictionary of all component instances attached to a specific entity.
        
        Args:
            entity_id: The ID of the entity.
            
        Returns:
            A dictionary where keys are component types and values are component instances.
        """
        self._entity_exists(entity_id)
        
        # Iterate through all component type dictionaries in _world
        return {comp_type: entities_with_comp[entity_id]
                for comp_type, entities_with_comp in self._world.items()
                if entity_id in entities_with_comp}
    
    def delete_entity(self, entity_id: int):
        """
        Deletes an entity and all its associated components from the world.
        
        Args:
            entity_id: The ID of the entity to delete.
        """
        self._entity_exists(entity_id)
        
        # Collect component types that will become empty after removing this entity's components
        component_types_to_clean_up: List[ComponentType] = []
        
        # Iterate through all component type dictionaries to remove the entity's components
        for comp_type, entities_with_comp in self._world.items():
            if entity_id in entities_with_comp:
                del entities_with_comp[entity_id]
                # If the component type's dictionary becomes empty after deletion, mark it for removal
                if not entities_with_comp:
                    component_types_to_clean_up.append(comp_type)
        
        # Remove empty component type dictionaries from _world to clean up memory
        for comp_type in component_types_to_clean_up:
            del self._world[comp_type] # Remove the empty defaultdict entry

        # Finally, remove the entity ID itself from the active entities set
        self._entities.remove(entity_id)


# --- Example Usage ---
if __name__ == "__main__":
    from dataclasses import dataclass

    # Define some example component classes
    @dataclass
    class Position:
        x: int
        y: int

    @dataclass
    class Velocity:
        dx: int
        dy: int
    
    @dataclass
    class Health:
        current: int
        max: int

    @dataclass
    class PlayerTag: # A "tag" component (just indicates presence)
        pass

    world = World()

    # Create entities
    player_entity = world.create_entity()
    enemy1_entity = world.create_entity()
    tree_entity = world.create_entity()
    enemy2_entity = world.create_entity()

    print(f"Created entities: Player={player_entity}, Enemy1={enemy1_entity}, Tree={tree_entity}, Enemy2={enemy2_entity}")

    # Add components
    world.add_component(player_entity, Position(x=10, y=20))
    world.add_component(player_entity, Velocity(dx=1, dy=0))
    world.add_component(player_entity, Health(current=100, max=100))
    world.add_component(player_entity, PlayerTag()) # Add a tag component

    world.add_component(enemy1_entity, Position(x=50, y=60))
    world.add_component(enemy1_entity, Health(current=50, max=50))

    world.add_component(tree_entity, Position(x=0, y=0))

    world.add_component(enemy2_entity, Position(x=70, y=80))
    world.add_component(enemy2_entity, Velocity(dx=-1, dy=0))
    world.add_component(enemy2_entity, Health(current=30, max=30))

    print("\n--- Querying Components ---")
    player_pos = world.get_component(player_entity, Position)
    print(f"Player Position: {player_pos}") # Should be Position(x=10, y=20)

    enemy1_vel = world.get_component(enemy1_entity, Velocity)
    print(f"Enemy1 Velocity: {enemy1_vel}") # Should be None (as Enemy1 doesn't have Velocity)

    # Get all components for an entity
    player_components = world.get_components_of(player_entity)
    print(f"Player Components: {player_components}")

    print("\n--- Querying Entities by Components ---")
    # Entities with Position
    pos_entities = world.get_entities_with(Position)
    print(f"Entities with Position: {pos_entities}") # Should be {0, 1, 2, 3} (all entities)

    # Entities with Position and Health
    pos_health_entities = world.get_entities_with(Position, Health)
    print(f"Entities with Position and Health: {pos_health_entities}") # Should be {0, 1, 3}

    # Entities with Position, Velocity, and Health
    moving_living_entities = world.get_entities_with(Position, Velocity, Health)
    print(f"Entities with Position, Velocity, Health: {moving_living_entities}") # Should be {0, 3} (Player and Enemy2)

    # Entities with PlayerTag and Position
    players = world.get_entities_with(PlayerTag, Position)
    print(f"Entities with PlayerTag and Position: {players}") # Should be {0} (Player)

    # Query for non-existent component
    class NonExistentComponent: pass
    non_existent_query = world.get_entities_with(NonExistentComponent)
    print(f"Entities with NonExistentComponent: {non_existent_query}") # Should be set()

    print("\n--- Removing Components ---")
    world.remove_component(enemy1_entity, Health)
    enemy1_health = world.get_component(enemy1_entity, Health)
    print(f"Enemy1 Health after removal: {enemy1_health}") # Should be None

    # Check if Health component type is still in _world (it should be, player and enemy2 still have it)
    print(f"Is Health component type still in _world? {Health in world._world}")

    # Remove PlayerTag from player_entity
    world.remove_component(player_entity, PlayerTag)
    print(f"Is PlayerTag component type still in _world? {PlayerTag in world._world}") # Should be False if only player had it

    print("\n--- Deleting Entities ---")
    print(f"Entities before delete_entity(enemy1_entity): {world._entities}")
    world.delete_entity(enemy1_entity)
    print(f"Entities after delete_entity(enemy1_entity): {world._entities}")

    # Try to access deleted entity (should raise error)
    try:
        world.get_component(enemy1_entity, Position)
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Verify that enemy1's components are completely gone and not in queries
    print(f"Entities with Position after enemy1 deletion: {world.get_entities_with(Position)}") # Should be {0, 2, 3} (no 1)
    print(f"World state for Position component: {world._world.get(Position)}") # Should not contain enemy1
    print(f"Full _world state: {world._world}") # Check for cleanup