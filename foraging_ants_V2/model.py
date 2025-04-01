"""
Foraging Ants Model
===================
A Mesa implementation of an ant colony foraging for food.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("../../mesa"))

import numpy as np

from mesa import Model
from agents import ForagingAnt, Food
from mesa.experimental.continuous_space import ContinuousSpace

class ForagingAntsModel(Model):
    """
    Foraging Ants model. 
    
    Handles agent creation, placement and scheduling. Ants leave the colony to search 
    for food, and upon finding it, they return to the colony while communicating the 
    food location to other ants they encounter.
    """

    def __init__(
        self,
        initial_ants=30,
        initial_food=10,
        width=100,
        height=100,
        speed=1,
        range_of_communication=10,
        ants_needed=5,
        seed=None,
    ):
        """Create a new Foraging Ant model.

        Args:
            initial_ants: Number of Ants in the simulation (default: 100)
            initial_food: Number of food sources in the simulation (default: 10)
            width: Width of the space (default: 100)
            height: Height of the space (default: 100)
            speed: How fast the Ants move (default: 1)
            range_of_communication: The range within which ants can communicate
            ants_needed: Number of ants needed to collect a food source
            seed: Random seed for reproducibility (default: None)

        Indirect parameters (not chosen in the graphic interface for clarity reasons):
            ant_search_radius: Radius within which ants can detect food
            food_collection_radius: Radius for counting ants around food

        """

        super().__init__(seed=seed)
        
        # Model parameters
        self.initial_ants = initial_ants
        self.initial_food = initial_food
        self.width = width
        self.height = height
        self.range_of_communication = range_of_communication
        self.ants_needed = ants_needed
        
        # Setup colony parameters
        self.colony_position = 5,5  # Colony at the right corner
        self.colony_radius = 5.0
        
        # Food collection parameters
        self.ant_search_radius = 2.0  # Radius within which ants can detect food
        self.food_collection_radius = 5.0  # Radius for counting ants around food
        
        # Statistics
        self.food_collected = 0
        
        # Set up the space
        self.space = ContinuousSpace(
            [[0, width], [0, height]],
            torus=True,
            random=self.random,
            n_agents=initial_ants + initial_food,
        )
        
        # Create and place the Ant agents
        ants_positions = self.rng.random(size=(self.initial_ants, 2)) * self.space.size
        directions = self.rng.uniform(-1, 1, size=(self.initial_ants, 2))
        ForagingAnt.create_agents(
            self,
            self.initial_ants,
            self.space,
            initial_position=ants_positions,
            direction=directions,
            speed=speed,
            range_of_communication=range_of_communication)


        # Create and place the Food agents - away from colony and each other
        possible_positions = []

        while len(possible_positions) < initial_food:
            pos = self.rng.random(2) * self.space.size
            if np.linalg.norm(pos - np.array(self.colony_position)) <= self.colony_radius * 3:
                continue
            if any(np.linalg.norm(pos - np.array(p)) < 10 for p in possible_positions):
                continue
            possible_positions.append(pos)
        
        food_positions = np.array(possible_positions)
        Food.create_agents(
            self, 
            initial_food,
            self.space,
            position = food_positions,
            ants_needed=ants_needed)


    def calculate_ant_angles(self):
        """Calculate angles for all ant agents for visualization."""
        ant_agents = [agent for agent in self.agents if isinstance(agent, ForagingAnt)]
        
        for ant in ant_agents:
            ant.angle = np.degrees(np.arctan2(ant.direction[1], ant.direction[0]))

    def step(self):
        """Run one step of the model."""
        self.agents.shuffle_do("step")
        self.calculate_ant_angles()
