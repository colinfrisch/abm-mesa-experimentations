"""
Mesa implementation of Virus/Antibody model: Agents module.
"""

import numpy as np
from collections import deque
import copy
import os
import sys

sys.path.insert(0, os.path.abspath("../../mesa"))

from mesa.experimental.continuous_space import ContinuousSpaceAgent


class AntibodyAgent(ContinuousSpaceAgent):
    """An Antibody agent. They move randomly until they see a virus, go fight it.
    If they lose, stay ko for a bit, lose health and back to random moving.
        """

    def __init__(
        self,
        model,
        space,
        sight_range,
        duplication_rate,
        ko_timeout,
        memory_capacity,
        initial_position=(0, 0),
        direction=(1, 1),        
    ):
        """Create a new Antibody agent.

        Args:
            model: Model instance the agent belongs to
            space: The space the agent is in
            position: Initial position of the agent
            speed: Distance to move per step
            direction: numpy vector for the Ant's direction of movement
            sight_range: The range within which the agent can communicate with others
            memory_capacity: The capacity of the ant's memory
            duplication_rate : The rate at which the antibody agents can duplicate 

        """

        super().__init__(model = model,space = space)
        
        # Antibody movements
        self.position = initial_position
        self.speed = 1.5
        self.direction = direction
        self.angle = 0.0 

        # Antibody characteristics
        self.sight_range = sight_range
        self.health = 2
        self.duplication_rate = duplication_rate
        

        # Antibody memory
        self.st_memory : deque = deque()
        self.lt_memory : list = [] 
        self.memory_capacity = memory_capacity
        
        # Antibody state
        self.target = None
        self.ko_timeout = ko_timeout
        self.ko_steps_left = 0


    def step(self):
        """A step in the ant's behavior."""        
        
        # Check for virus at length of sight
        if self.target == None:
            closest_virus = self.find_closest_virus() #agent
            if closest_virus is not None:
                self.target = closest_virus
            
        self.communicate()
        
        if self.random.random() < self.duplication_rate :
            self.duplicate()
        self.move()
    

    def duplicate(self):
        duplicate = AntibodyAgent.create_agents(
            self.model, 
            1,
            self.space,
            initial_position = self.position,
            direction=(1, 1),
            sight_range = self.sight_range,
            memory_capacity=self.memory_capacity,
            duplication_rate = self.duplication_rate,
            ko_timeout = self.ko_timeout
            )[0]
        
        duplicate.st_memory = deque([item for item in self.st_memory])
        duplicate.lt_memory = [item for item in self.st_memory]

        duplicate.target = None
        duplicate.ko_steps_left = 0
        print('duplicated antibody', duplicate.st_memory)
    


    def find_closest_virus(self) -> "VirusAgent":
        """
        Returns the closest VirusAgent within sight range.
        """
        nearby_agents = self.space.get_agents_in_radius(self.position, self.sight_range)[0]
        closest_viruses = [agent for agent in nearby_agents if isinstance(agent, VirusAgent)]

        if not closest_viruses:
            return None

        return closest_viruses[0]



    
    def communicate(self) -> bool:
        """Share the DNA info to st and lt memory of nearby external antibody"""
        nearby_agents = self.space.get_agents_in_radius(self.position, self.sight_range)[0]
        nearby_antibodies = [agent 
                             for agent 
                             in nearby_agents
                             if isinstance(agent, AntibodyAgent) and agent.unique_id != self.unique_id]

        if nearby_antibodies == []:
            return False
        
        for external_antibody in nearby_antibodies:
            external_antibody.st_memory = deque([[item 
                                                for item 
                                                in self.st_memory 
                                                if item not in external_antibody.lt_memory]])
            
            external_antibody.lt_memory = external_antibody.lt_memory + [item 
                                                                         for item 
                                                                         in self.st_memory 
                                                                         if item not in external_antibody.lt_memory]
        return True


    def move(self):
        """
        Move the antibody based on its current target (3 possibilities). 
        - no target, move randomly
        - virus as target, move towards it
        - self as target, stays idle (ko)
        """

        new_pos = None

        if self.target == self : # the antibody fought a virus and lost, but he's still alive. So he's unable to move for a few steps
            self.ko_steps_left -=1
            if self.ko_steps_left == 0 :
                self.target = None

        elif not self.target:  # Random movement with some directional persistence
            self.direction = self.direction + np.array([self.random.uniform(-0.5, 0.5), self.random.uniform(-0.5, 0.5)])
            norm = np.linalg.norm(self.direction)
            if norm > 0:
                self.direction = self.direction / norm
            new_pos = self.position + self.direction * self.speed

        elif self.target and self.target.space: # Move towards target (virus)
            try :
                vector_to_target = np.array(self.target.position) - np.array(self.position)
                distance = np.linalg.norm(vector_to_target)
                if distance > self.speed: # Normalize and scale by speed
                    self.direction = vector_to_target / distance
                    new_pos = self.position + self.direction * self.speed
                else: # The antibody reached the virus
                    self.engage_virus(self.target)
            except Exception as e:
                print(e, self.target.unique_id)
                self.target = None
                return
        
        else: # The target is not in the space anymore (it was killed by the antibody)
            self.target = None
            return

        # Move the agent
        try :
            if new_pos is not None and self is not None:
                self.position = new_pos
        except Exception as e:
            print(e, self.unique_id)
            return
        
    def engage_virus(self,virus_to_engage) -> str:
        """if the antibody has the DNA info of the virus stored (in st or lt memory), the antibody wins, else the virus wins"""
            # First check if the virus still exists
        if virus_to_engage not in self.model.agents:
            self.target = None
            return 'no_target' 

        virus_to_engage_dna = copy.deepcopy(virus_to_engage.dna)
        if virus_to_engage_dna in self.st_memory or virus_to_engage_dna in self.lt_memory : # antibody wins and kills the virus
            print('killed virus', virus_to_engage_dna, self.st_memory, self.lt_memory, self.health)
            virus_to_engage.remove()
            self.target = None
            return 'win'

        else : # ko for a few steps (can't move) AND stores virus dna in st+lt but if already has low health => dies
            print('beaten', self.health)
            self.health -= 1
            print(self.health)

            if self.health == 0:
                self.remove()
                self.model.schedule.remove(self)
                return 'dead'
            
            self.st_memory.append(virus_to_engage_dna)
            self.lt_memory.append(virus_to_engage_dna)
            self.ko_steps_left = self.ko_timeout
            self.target = self

            print(self.st_memory, self.lt_memory)
            return 'ko'



class VirusAgent(ContinuousSpaceAgent):
    """A virus agent.

    These agents move randomly. They are passive and simply mutate. The 'fighting with antibodies' 
    part is handled in the AntibodyAgent class. They can duplicate themselves with a chance of 
    mutation. They cannot overlap each other in the space.
    """

    def __init__(
        self,
        model,
        space,
        mutation_rate,
        duplication_rate,
        dna = None,
        position=(0, 0), 
        ):
        """Create a new Virus agent.

        Args:
            model: Model instance the agent belongs to
            space: The space the agent is in
            position: Initial position of the agent
            mutation_rate: Probability of mutation during reproduction
            duplication_rate: Probability of duplication
        """

        super().__init__(model = model,space = space)

        self.position = position
        self.mutation_rate = mutation_rate
        self.duplication_rate = duplication_rate
        self.speed = 1
        self.direction = (1, 1)

        if dna == None :
            self.dna = self.generate_dna()
        else : 
            self.dna = dna
        
    def step(self):
        """Virus movement and duplication."""
        if self.random.random() < self.duplication_rate:
            #print('duplicating', rand, self.duplication_rate, rand < self.duplication_rate)
            self.duplicate()
        self.move()
    
    def duplicate(self):
        """Duplicate the virus agent."""
        if self is None or self.space is None:
            return
        
        VirusAgent.create_agents(
            self.model,
            1,
            self.space,
            position=self.position,
            mutation_rate=self.mutation_rate,
            duplication_rate=self.duplication_rate,
            dna = self.generate_dna(self.dna)
        )[0]
     
    def generate_dna(self, dna=None):
        """
        Generate a DNA sequence based on input : a list of 3 integers between 0 and 9.
        If dna is None, a new DNA sequence is generated.
        If dna is provided, it is mutated based on the mutation rate.
        """
        if dna is None:
            return [self.random.randint(0, 9) for _ in range(3)]
        
        else: 
            
            index = self.random.randint(0, 2)
            chance = self.random.random()
            if chance < self.mutation_rate/2:
                dna[index] = (dna[index] + 1) % 10
            elif chance < self.mutation_rate :
                dna[index] = (dna[index] - 1) % 10
            
            return dna
        
    def move(self):
        """
        Move the virus (always randomly).
        """

        new_pos = None
    
        self.direction = self.direction + np.array([self.random.uniform(-0.5, 0.5), self.random.uniform(-0.5, 0.5)])
        norm = np.linalg.norm(self.direction)
        if norm > 0:
            self.direction = self.direction / norm
        
        if self is not None and self.space is not None:
            if self.position is not None:
                try :
                    new_pos = self.position + self.direction * self.speed
                    self.position = new_pos
                except Exception as e:
                    print(e, self.unique_id)
                    return
                