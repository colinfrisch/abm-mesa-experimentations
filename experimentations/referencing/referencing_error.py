import os
import sys
sys.path.insert(0, os.path.abspath("../../mesa"))

from mesa import Model
from mesa.experimental.continuous_space import ContinuousSpace, ContinuousSpaceAgent

class SimpleAgent(ContinuousSpaceAgent):
    def __init__(self, model, space):
        super().__init__(model=model, space=space)
        self.position = (0, 0)
        self.target = None
    
    def step(self):
        # Find a target if needed
        if self.target is None and len(self.model.agents_list) > 1:
            self.target = [a for a in self.model.agents_list if a != self][0]
            print(f"Agent {self.unique_id} targets {self.target.unique_id}")
        
        # Show status and remove if first agent
        if self.target:
            print(f"Target space: {self.target.space}")
            if self.unique_id == 1 and self.target.space is not None:
                print(f"Removing target")
                self.model.agents_list.remove(self.target)
                self.target.remove()
                # We don't set self.target = None - this causes the error
            
            # Detect the error condition
            if self.target and self.target.space is None:
                print(f"Target exists but space is None ***********************")

class SimpleModel(Model):
    def __init__(self):
        super().__init__()
        self.space = ContinuousSpace([[0, 10], [0, 10]], torus=True, random=self.random)
        self.agents_list = []
        
        # Create 2 agents
        for _ in range(2):
            agent = SimpleAgent(self, self.space)
            self.agents_list.append(agent)
    
    def step(self):
        for agent in list(self.agents_list):
            agent.step()

# Run the model
if __name__ == "__main__":
    model = SimpleModel()
    model.step()  # First agent targets second agent
