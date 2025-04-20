from langgraph.graph import StateGraph
from typing import TypedDict

class Memory():
    pass


class GraphCoT():
    def __init__(self, model):
        self.model = model
        self.memory = Memory(agent=self, model=model)
        self.graph = self._build_graph()

    def _cot_node(self, state: dict) -> dict:
        thought = f"Let's think step by step to answer: {state['input']}"
        self.memory.remember_short_term(
            model=self,
            entry_content=thought,
            entry_type="reasoning"
        )
        answer = self.get_answer_from_llm(thought) 
        self.memory.remember_short_term(
            model=self,
            entry_content=answer,
            entry_type="final_answer"
        )
        state["output"] = answer
        return state

    def _build_graph(self):
        builder = StateGraph(dict)
        builder.add_node("cot", self._cot_node)
        builder.set_entry_point("cot")
        builder.set_finish_point("cot")
        return builder.compile()

    def run(self, query: str) -> dict:
        return self.graph.invoke({"input": query})
    



    def get_answer_from_llm(self, thought: str) -> str:
        # Simulate getting an answer from a language model
        return f"Answer to '{thought}'"
