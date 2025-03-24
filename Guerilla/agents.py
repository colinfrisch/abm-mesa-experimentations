import os
import sys
import math

mesa_path = os.path.abspath("/Users/colinfrisch/Desktop/mesa")
if mesa_path not in sys.path:
    sys.path.insert(0, mesa_path)
    
from mesa.discrete_space import CellAgent



class SoldierAgent(CellAgent):
    """The base animal class."""

    def __init__(
        self, model, side : bool, fire_power : float, sight : int, cell = None
    ):
        """Initialize an soldier.

        Args:
            model: Model instance
            side : army or guerilla
            fire_power : probability of killing an enemy when shooting
            sight : distance of sight
            cell: Cell in which the soldier starts
        """
        super().__init__(model)
        self.side = side
        self.fire_power = fire_power
        self.sight = sight
        self.cell = cell
        if cell:
            self.pos = cell.coordinate
    
    def manhattan_distance(self,agent):
        x1, y1 = self.pos
        x2, y2 = agent.pos
        return abs(x1 - x2) + abs(y1 - y2)

    def find_closest_enemy(self,agent_side):
        enemy_agents = [agent for agent in self.model.agents if agent.side != agent_side]

        if not enemy_agents:
            return None

        closest_enemy = min(enemy_agents, key= lambda agent : self.manhattan_distance(agent=agent))
        return closest_enemy
    

    def shoot(self,enemy):
        """If possible, shoot at enemy soldier at sight distance."""

        if self.random.random() < self.fire_power:
            enemy.remove()


    def move(self,closest_enemy):
        """Move towards the closest cell with an enemy soldier"""
        neighborhood = [cell for cell in self.cell.neighborhood]

        dx = closest_enemy.pos[0] - self.pos[0]
        dy = closest_enemy.pos[1] - self.pos[1]

        if dx == 0 and dy == 0:
            return (0, 0)

        # Normalize the direction vector
        distance = math.hypot(dx, dy)
        ux, uy = dx / distance, dy / distance

        # Choose the direction with the highest dot product
        target_cell = max(
            neighborhood,
            key=lambda cell: cell.coordinate[0]*ux + cell.coordinate[1]*uy  # dot product
        )

        self.cell = target_cell
        self.pos = target_cell.coordinate

    
    def step(self):
        """if there is an enemy soldier in sight, shoot at it, else move"""

        closest_enemy = self.find_closest_enemy(self.side)
        #print(closest_enemy)
        #print(self.manhattan_distance(closest_enemy))

        if self.manhattan_distance(closest_enemy)<self.sight :
            self.shoot(closest_enemy)
        else :
            self.move(closest_enemy)



