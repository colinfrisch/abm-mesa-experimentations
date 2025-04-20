from abc import ABC, abstractmethod
from typing import Callable
from dataclasses import dataclass
import json
from llm_agent import LLMAgent, Model
from module_llm import ModuleLLM
from reasoning import Reasoning

@dataclass
class Observation:
    """Snapshot of everything the agent can see this step."""
    step: int
    self_state: dict
    local_state: dict          # neighbours within vision radius
    global_keys: dict          # optional, could be linked with Observables experimental feature in mesa

@dataclass
class Plan:
    """LLM‑generated plan that can span ≥1 steps."""
    thoughts: list[str]      # full scratch‑pad, useful for logging
    actions: list[dict]      # JSON‑serialised function calls
    ttl: int = 1             # steps until re‑planning (ReWOO sets >1)

class Paradigm(ABC):
    """Glues together observation, planning, memory & action execution."""
    def __init__(
        self,
        llm:         ModuleLLM,
        reasoning:     "Reasoning",
        tool_schema: dict[str, Callable],   # name -> python fn
        max_tokens:  int = 1024,
    ):
        self.llm          = llm
        self.reasoning      = reasoning
        self.tool_schema  = tool_schema
        self.max_tokens   = max_tokens
        self._cached_plan = None           # reused when ttl>1


    def step(self, agent: "LLMAgent", model: "Model"):
        if self._cached_plan and self._cached_plan.ttl > 0:
            self._cached_plan.ttl -= 1
            plan = self._cached_plan
        else:
            obs  = self.observe(agent, model)
            plan = self.reasoning.plan(obs, agent.memory, self.llm, self.max_tokens)
            self._cached_plan = plan  # may be reused by ReWOO

        self.action(plan, agent, model)

    # ---------- DEFAULT HOOKS TO OVERRIDE IF NEEDED ----------
    def observe(self, agent, model) -> Observation:
        """Paradigm‑specific view"""
        neighbors = agent.space.get_agents_in_radius(agent.position, radius=1)
        return Observation(
            step=model.steps(),
            self_state={...}, #code with memory
            local_state={...}, # code with local variables and neighbours
            global_keys={...}, # code with global variables
        )

    def action(self, plan: Plan, agent, model):
        """Decode each action dict and call ⟦model.apply_action()⟧."""
        for action in plan.actions:
            if action["tool"] not in self.tool_schema:
                continue          # ignore illegal actions
            self.tool_schema[action["tool"]](agent, model, **action)


class ClassBasedParadigm(Paradigm):
    """Class-based action execution: agent methods are called directly.
    Uses the defaut observe() method to generate the observation.
    """
    def observe(self, agent, model):
        return super().observe(agent, model)

    def action(self, plan, agent, model):
        for act in plan.actions:
            if act["tool"] == "move":
                new_pos = (agent.pos[0] + act["dx"], agent.pos[1] + act["dy"])
                model.apply_action_move(agent, new_pos)
            elif act["tool"] == "eat":
                model.apply_action_eat(agent)

class FunctionBasedParadigm(Paradigm):
    def action(self, plan, agent, model):
        for act in plan.actions:
            fn = self.tool_schema.get(act["tool"])
            if fn:                          # pure function
                fn(model_state=model, agent_id=agent.unique_id, **act)

