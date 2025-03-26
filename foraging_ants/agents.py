"""
Mesa implementation of Foraging Ants model: Agents module.
"""

import numpy as np
import os
from memory_module.memory import Memory
import sys

sys.path.insert(0, os.path.abspath("../../mesa"))

from mesa.experimental.continuous_space import ContinuousSpaceAgent

# Incoherences in get_neighbors method, replaced by get_agents_in_radius

class ForagingAnt(ContinuousSpaceAgent):
    """An Ant agent.

    These agents move randomly. They have a memory capacity to store recent 
    food source locations. Ants forget the oldest memories when their memory 
    capacity is exceeded. They can overlap each other in the space.
    """

    def __init__(
        self,
        model,
        space,
        initial_position=(0, 0),
        speed=1,
        direction=(1, 1),
        range_of_communication=10,
        memory_capacity=10
    ):
        """Create a new Ant agent.

        Args:
            model: Model instance the agent belongs to
            space: The space the agent is in
            position: Initial position of the agent
            speed: Distance to move per step
            direction: numpy vector for the Ant's direction of movement
            range_of_communication: The range within which the agent can communicate with others
            memory_capacity: The capacity of the ant's memory
        """

        super().__init__(space, model)
        self.position = initial_position
        self.speed = speed
        self.direction = direction
        self.range_of_communication = range_of_communication
        self.angle = 0.0  # represents the angle at which the ant is moving
        self.memory = Memory(model, agent_id=self.unique_id, capacity=memory_capacity)
        
        # Ant state
        self.mode = "explore"  # Modes: "explore", "return_to_colony", "go_to_food"
        self.target = None


    def step(self):
        """A step in the ant's behavior."""        
        
        # Check for food at current position
        if self.mode == "explore":
            food_here = self.check_for_food()

            if food_here is not None:
                self.mode = "return_to_colony"
                self.memory.remember(entry_content=food_here, entry_type="food")
                self.target = self.model.colony_position
            
            elif self.memory.get_by_type("food") != []:
                self.mode = "go_to_food"
                latest_food = self.memory.memory_storage[self.memory.get_by_type("food")[-1]]["entry_content"]
                self.target = latest_food

        else :
            self.communicate()
        
        self.move()
    

    def check_for_food(self):
        """Check if there is food at the current position."""
        food_sources = [agent for agent in self.space.get_agents_in_radius(
            self.position, self.model.ant_search_radius)[0] 
            if isinstance(agent, Food)]
        
        if food_sources != []:
            return food_sources[0].pos
        return None
    
    
    def near_target(self):
        """Check if the ant is near its target."""
        if self.target is None:
            return False
        distance = np.sqrt(np.sum((np.array(self.position) - np.array(self.target))**2))
        return distance < 1.0  # Threshold distance to be considered "near"

    
    def communicate(self):
        """Share food location information with nearby ants that are available (explore mode)."""
        
        if self.mode in ["return_to_colony", "go_to_food"]:
            nearby_available_ants = [ant_agent for ant_agent in self.space.get_agents_in_radius(
                self.position, self.range_of_communication)[0]
                if isinstance(ant_agent, ForagingAnt) and ant_agent.unique_id != self.unique_id and ant_agent.mode == "explore"]
            
            
            # Share food location with nearby ants. An ant can only have one food memory at a time.
            food_memories_ids = self.memory.get_by_type("food")
            if food_memories_ids != [] and nearby_available_ants != []:
                for external_ant in nearby_available_ants:
                    #///!!!\\\ remove useless variable
                    new_entry_key=self.memory.tell_to(entry_id = food_memories_ids[0],external_agent = external_ant)


    def move(self):
        """Move the ant based on its current mode."""

        new_pos = None
        food_memories_index = self.memory.get_by_type("food")
        
        if self.mode == "explore": # Explore for food and available for communication

            # Random movement with some directional persistence
            self.direction = self.direction + np.array([self.random.uniform(-0.5, 0.5), self.random.uniform(-0.5, 0.5)])
            # Normalize direction
            norm = np.linalg.norm(self.direction)
            if norm > 0:
                self.direction = self.direction / norm
            
            new_pos = self.position + self.direction * self.speed


        elif self.mode in ["return_to_colony", "go_to_food"]:
            if self.target is not None:
                # Move towards target (colony or food)
                vector_to_target = np.array(self.target) - np.array(self.position)
                distance = np.linalg.norm(vector_to_target)
                
                if distance > self.speed:
                    # Normalize and scale by speed
                    self.direction = vector_to_target / distance
                    new_pos = self.position + self.direction * self.speed
                
                else:
                    # We've reached our target
                    new_pos = self.target
                    
                    # Update mode if reached target
                    if self.mode == "return_to_colony":
                        # If we have memory of food, go to it, else (re)start exploring

                        if food_memories_index:
                            latest_food = self.memory.memory_storage[food_memories_index[-1]]["entry_content"]
                            self.target = latest_food
                            self.mode = "go_to_food"
                        else:
                            self.mode = "explore"
                            self.target = None
                    
                    elif self.mode == "go_to_food" and self.near_target():
                        # If near food target, switch to exploring (which will find the food)

                        nearby_food = [agent for agent in self.space.get_agents_in_radius(
                            self.position, self.model.ant_search_radius)[0] 
                            if isinstance(agent, Food)]

                        if not nearby_food: #back to exploring, and forget previous food memories
                            self.mode = "explore"
                            for food_memory in food_memories_index:
                                self.memory.forget(food_memory)
                            
        
        # Move the agent
        if new_pos is not None:
            self.position = new_pos
            
            # Calculate angle for visualization
            self.angle = np.degrees(np.arctan2(self.direction[1], self.direction[0]))


class Food(ContinuousSpaceAgent):
    """A food agent.

    Spawns randomly, and is collected when a precise number of ants gather
    around it. There is always a constant number in the grid. 
    """

    def __init__(
        self,
        model,
        space,
        position=(0, 0),
        ants_needed=5,
    ):
        """Create a new Food agent.

        Args:
            model: Model instance the agent belongs to
            space: The space the agent is in
            position: Initial position of the agent
            ants_needed: The number of ants needed to gather around the food
        """
        super().__init__(space, model)
        self.position = position
        self.ants_needed = ants_needed
        self.neighbors = []

    def step(self):
        """Update the list of neighbors for visualization purposes."""
        self.neighbors = self.space.get_agents_in_radius(self.position, self.model.food_collection_radius)[0]
        nearby_ants = [agent for agent in self.neighbors if isinstance(agent, ForagingAnt)]

        if len(nearby_ants) >= self.ants_needed:
            # If enough ants, remove the food and spawn a new one
            self.remove()
            self.model.food_collected +=1