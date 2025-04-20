from typing import Any, List, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass
from paradigm import ClassBasedParadigm, FunctionBasedParadigm
from reasoning import CoTReasoning, ReActReasoning, ReWOOReasoning

class Agent():
    pass
class Memory():
    pass
class Model():
    pass
def reasoning_compatibility():
    pass

model = Model()


class LLMAgent(Agent):
    def __init__(self, 
                 paradigm : str, 
                 reasoning : str, 
                 model : Model, 
                 memory : Memory, 
                 tools = None):
        
        self.paradigm_types = {
            "class_based": ClassBasedParadigm,
            "function_based": FunctionBasedParadigm
        }

        self.reasoning_types = {
            "chain_of_thought": CoTReasoning,
            "ReAct": ReActReasoning,
            "ReWOO": ReWOOReasoning
        }
        
        self.paradigm = self.paradigm_types[paradigm](model, memory, reasoning, tools)
        self.reasoning = self.reasoning_types[reasoning]()
        self.model = model
        self.memory = memory
        self.tools = tools

    ...


#---------------------------------------------------------------------------------------

myLLMAgent = LLMAgent(
    reasoning = "chain_of_thought",
    paradigm = "class_based",
    model = model,
    tools = None
)

