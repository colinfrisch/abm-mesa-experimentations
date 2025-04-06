"""
Guerilla prediction model. Made to verify the Square Law (Lanchester) and modified asymmetric model (Deitchman adaptation).
"""

import math
import os
import sys
from guerilla.agents import SoldierAgent
from guerilla.ruling_equations import calculate_Lanchester, calculate_Deitchman

mesa_path = os.path.abspath("/Users/colinfrisch/Desktop/mesa")
if mesa_path not in sys.path:
    sys.path.insert(0, mesa_path)

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalVonNeumannGrid
from mesa.experimental.devs import ABMSimulator


class GuerillaModel(Model):
    """Guerilla simulation Model.

    A model for simulating the different aspects of a guerilla and compare them to the different theoretical models.
    """

    description = (
        "A model for simulating the different aspects of a guerilla and compare them to the different theoretical models."
    )

    def __init__(
        self,
        width=20,
        height=20,
        situation=0,
        starting_personnel_army=100,
        starting_personnel_guerilla=50,
        army_fire_power=0.5,
        guerilla_fire_power=0.5,
        army_sight=1,
        guerilla_sight=1,
        seed=None,
        simulator: ABMSimulator = None,
    ):
        """Create a new Wolf-Sheep model with the given parameters depending on the situation (classic or ambush).

        Args:
            height: Height of the grid
            width: Width of the grid
            
            situation : classic (front to front battle) or ambush,
            starting_personnel_army : number of soldiers in the army at the beginning
            starting_personnel_guerilla : number of soldiers in the guerilla at the beginning
            army_fire_power : probability of killing an enemy when shooting for the army
            guerilla_fire_power : probability of killing an enemy when shooting for the guerilla
            army_sight : distance of sight for the army
            guerilla_sight : distance of sight for the guerilla
            seed: Random seed
            simulator: ABMSimulator instance for event scheduling
        """
        super().__init__(seed=seed)
        self.simulator = simulator
        self.simulator.setup(self)
        self.situation = "Classic" if situation == 0 else "Ambush"
        self.calculate_Lanchester = calculate_Lanchester
        self.calculate_Deitchman = calculate_Deitchman

        # Initialize model parameters
        self.height = height
        self.width = width

        # Create grid using experimental cell space
        self.grid = OrthogonalVonNeumannGrid(
            [self.height, self.width],
            torus=False,
            capacity=math.inf,
            random=self.random,
        )

        # Set up data collection
        model_reporters = {
            "TotalSoldiers" : lambda m: len(m.agents_by_type[SoldierAgent]),
            "ArmySoldiers": lambda m: len([agent for agent in m.agents if agent.side == "Army"]),
            "GuerillaSoldiers": lambda m: len([agent for agent in m.agents if agent.side == "Guerilla"]),
            "ArmyLanchesterEquation": lambda m: m.calculate_Lanchester(initial_army_personnel = starting_personnel_army, 
                                                                        step = m.steps, 
                                                                        fire_power = army_fire_power, 
                                                                        sight = army_sight),
            "GuerillaLanchesterEquation": lambda m: m.calculate_Lanchester(initial_army_personnel = starting_personnel_guerilla,
                                                                        step = m.steps,
                                                                        fire_power = guerilla_fire_power,
                                                                        sight = guerilla_sight),
            "ArmyDeitchmanEquation": lambda m: m.calculate_Deitchman(initial_army_personnel = starting_personnel_army,
                                                                        step = m.steps,
                                                                        fire_power = army_fire_power,
                                                                        sight = army_sight,
                                                                        side = "ambushed"),
            "GuerillaDeitchmanEquation": lambda m: m.calculate_Deitchman(initial_army_personnel = starting_personnel_guerilla,
                                                                        step = m.steps,
                                                                        fire_power = guerilla_fire_power,
                                                                        sight = guerilla_sight,
                                                                        side = "ambusher"),
    
        }

        self.datacollector = DataCollector(model_reporters)

        print(self.situation,'---------------------------------------------------------------')
        SoldierAgent.create_agents(
            self,
            starting_personnel_army,
            fire_power=army_fire_power,
            sight=army_sight,
            side="Army",
            cell = self.soldier_placement(situation=self.situation, side="Army", personnel=starting_personnel_army)
        )

        SoldierAgent.create_agents(
            self,
            starting_personnel_guerilla,
            fire_power=guerilla_fire_power,
            sight=guerilla_sight,
            side="Guerilla",
            cell = self.soldier_placement(situation=self.situation, side="Guerilla", personnel=starting_personnel_guerilla)
        )

        

        # Collect initial data
        self.running = True
        self.datacollector.collect(self)


    def soldier_placement(self,situation, side, personnel):
        """At the beginning of the simulation, place the soldiers in the grid depending on their side and the situation."""

        if side not in {"Army", "Guerilla"} or situation not in {"Classic", "Ambush"}:
            raise ValueError("Side must be 'Army' or 'Guerilla', situation 'Classic' or 'Ambush'")

        # In a classic situation, the two forces start facing to face (on opposite sides of the grid)
        # We first try to place all the soldiers in the front row, then if there isnt enough space : in the second row, than third, etc. 
        if self.situation == "Classic":
            row = 1 if side == "Army" else self.height - 2
            step = 1 if side == "Army" else -1
            occupied_area = [cell for cell in self.grid.all_cells.cells if cell.coordinate[1] == row]

            while len(occupied_area) < personnel:
                occupied_area += [cell for cell in self.grid.all_cells.cells if cell.coordinate[1] == row]
                row += step

        
        # In an ambush situation, the guerilla force is circling the army force
        # Using the same logic as above, we try to place all the army sodiers starting from the middle, and all the guerilla soldiers starting from the edges
        else : #self.situation == "Ambush" 
            if side == "Army":
                layer = 0
                center_x, center_y = self.width // 2, self.height // 2
                occupied_area = [cell for cell in self.grid.all_cells.cells
                                    if center_x - layer <= cell.coordinate[0] <= center_x + layer
                                    and center_y - layer <= cell.coordinate[1] <= center_y + layer]

                while len(occupied_area) < personnel:
                    occupied_area += [cell for cell in self.grid.all_cells.cells
                                    if center_x - layer <= cell.coordinate[0] <= center_x + layer
                                    and center_y - layer <= cell.coordinate[1] <= center_y + layer]
                    layer += 1

            else: #guerilla
                layer = 0
                occupied_area = [cell for cell in self.grid.all_cells.cells
                                    if cell.coordinate[0] in {layer, self.width - 1 - layer} or
                                        cell.coordinate[1] in {layer, self.height - 1 - layer}]

                while len(occupied_area) < personnel:
                    occupied_area += [cell for cell in self.grid.all_cells.cells
                                    if cell.coordinate[0] in {layer, self.width - 1 - layer} or
                                        cell.coordinate[1] in {layer, self.height - 1 - layer}]
                    layer += 1
                
        
        return self.random.choices(occupied_area, k=personnel)
    


    def step(self):
        """Execute one step of the model."""
        # activate all agents
        self.agents.shuffle_do("step")

        # Collect data
        self.datacollector.collect(self)
