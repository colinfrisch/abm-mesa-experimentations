from abc import ABC, abstractmethod
from typing import Callable
from paradigm import Observation, Plan
from memory import Memory
from module_llm import ModuleLLM
import json

class Reasoning(ABC):
    def __init__(self,
                SYSTEM_PROMPT: str,
                TOOLS_SCHEMA: dict[str, Callable],
                 ):
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.TOOLS_SCHEMA  = TOOLS_SCHEMA
    
    @abstractmethod
    def plan(
        self,
        obs: Observation,
        memory: Memory,
        llm: ModuleLLM,
        max_tokens:int,
    ) -> Plan: ...


    def _format_observation(self, observation: Observation, memory: Memory) -> str: 
        """Format the observation for the LLM.  Default: JSON."""
        ...

    def _format_initial_state(self, memory: Memory) -> list[dict]: 
        """Format the state to be prompatble for the LLM.  Default: JSON."""
        ...


class CoTReasoning(Reasoning):
    """
    Chain-of-Thought (CoT) reasoning : LLM is prompted to think step by step.

    system prompt example:
    SYSTEM_PROMPT = "You are an agent in a simulation. Think step by step...
                        Return JSON: { "thoughts": [...], "actions": [...] }"
    """
    def __init__(self):
        super().__init__()

    def plan(self, obs, memory, llm, max_tokens):
        prompt = [
          {"role":"system", "content": self.SYSTEM_PROMPT},
          {"role":"user",   "content": self._format_observation(obs, memory)}
        ]
        rsp = llm.generate(messages=prompt, max_tokens=max_tokens,
                           response_format   = "json_object",
                           tool_schema       = self.TOOLS_SCHEMA)  # ← JSON schema
        data = json.loads(rsp)
        return Plan(thoughts=data["thoughts"], actions=data["actions"], ttl=1)
    

class ReActReasoning(Reasoning):
    def __init__(self):
        super().__init__()

    MAX_TURNS = 4
    def plan(self, obs, memory, llm, max_tokens):
        transcript, actions = [], []
        state = self._initial_state(obs, memory)
        for _ in range(self.MAX_TURNS):
            rsp = llm.generate(
                messages=state,
                max_tokens=max_tokens,
                response_format="json_object",
                tool_schema=self.TOOLS_SCHEMA
            )
            data = json.loads(rsp)
            transcript.append(data["thought"])
            if data["action"]["tool"] == "finish":
                break
            actions.append(data["action"])
            # get observation for the executed action and append to messages
            obs_reply = self._simulate_action_for_llm(data["action"])
            state += [
              {"role":"assistant","content":rsp},
              {"role":"user","content":obs_reply}
            ]
        return Plan(thoughts=transcript, actions=actions, ttl=1)


class ReWOOReasoning(Reasoning):
    def __init__(self):
        super().__init__()

    def plan(self, obs, memory, llm, max_tokens):
        prompt = [...]
        rsp = llm.generate(..., response_format="json_object", tool_schema=self.TOOLS_SCHEMA)
        data = json.loads(rsp)
        ttl  = max(1, int(data.get("duration_steps", 1)))
        return Plan(thoughts=data["rationale"], actions=data["actions"], ttl=ttl)
