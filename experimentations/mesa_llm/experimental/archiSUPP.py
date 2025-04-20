paradigm.py
├── class Observation                                     ← empty shell
├── class Plan                                            ← empty shell
│
├── class Paradigm
│   ├── __init__()                                        ← init logic
│   ├── step()                                            ← main loop
│   ├── observe()                                         ← overridden
│   └── action()                                          ← overridden
│
├── class ClassBasedParadigm(Paradigm)
│   ├── observe()                                         ← custom class logic
│   └── action()                                          ← custom class logic
│
└── class FunctionBasedParadigm(Paradigm)
    └── action()                                          ← custom function logic


reasoning.py
├── class Reasoning
│   └── plan()                                            ← base plan method
│
├── class CoTReasoning(Reasoning)
│   ├── __init__()                                        ← prompt setup
│   └── plan()                                            ← chain-of-thought planning
│   └── SYSTEM_PROMPT                                     ← CoT system prompt
│
├── class ReActReasoning(Reasoning)
│   └── plan()                                            ← ReAct loop
│   └── MAX_TURNS                                         ← max reasoning steps
│
└── class ReWOOReasoning(Reasoning)
    └── plan()                                            ← ReWOO planner
