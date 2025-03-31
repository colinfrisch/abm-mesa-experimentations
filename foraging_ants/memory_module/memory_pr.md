# Add agent memory module for storing and retrieving information

## Summary
This PR introduces a new Memory module that enables agents to store, recall, and share information during simulations. The memory system provides a simple yet powerful way to add memory capabilities to any Mesa agent with minimal implementation overhead.

## Key features
- Capacity-limited FIFO memory storage with automatic management
- Flexible entry types for any kind of information
- Timestamped entries tied to simulation steps
- Inter-agent memory sharing capabilities
- Efficient retrieval by entry type
- Selective memory removal

## Use cases
- Agents that need to recall previous states or observations
- Learning agents that improve behavior based on past experiences
- Communicating agents that exchange information
- Social simulations with belief or knowledge systems
- Resource-aware agents with memory constraints

## Example usage

```python
# Creating a memory for an agent
agent.memory = Memory(model=self.model, agent_id=self.unique_id, capacity=10)

# Storing information
position_entry_id = agent.memory.remember(
    entry_content=[10, 20],
    entry_type="position"
)

# Recalling information
position_data = agent.memory.recall(position_entry_id)

# Finding entries by type
all_position_entries = agent.memory.get_by_type("position")

# Sharing memory with another agent
agent.memory.tell_to(position_entry_id, other_agent)

# Removing an entry
agent.memory.forget(position_entry_id)
```

This implementation maintains simplicity while providing powerful capabilities for modeling memory-based agent behaviors.