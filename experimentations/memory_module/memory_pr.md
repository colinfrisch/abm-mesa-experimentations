# Memory PR upgrade

## About the upgrade

Switching to a object format for optimized storage : MemoryEntry is now an object. One of the perks of using an object is not being obligated to have a uniqueID creation module as an object already has an intrinsic uniqueid ```id(my_object)```. It saves storage space as well as lines of code.

##### ShortTermMemory : more memory-efficient and reactive (efficient store and pop functionality)
- Holds fixed number of recent MemoryEntry objects (automatic removing with dque)
- Optimized for quick retrieval of recent interactions similar to the previous proposition : ```get()```, ```get_by_entry_type()```, etc.
- Can be cleared/reset when an agent session ends

##### LongTermMemory : more computational-efficient (efficient navigation)
- Hash map storage for better organization 
- Can be searched (soon, still working on it... I'd greatly appreciate your feedbacks and ideas)


##### Justification of memory transfering
```tell_to()``` feature still here implemented directly in the memory (yay), but rename it ```communicate()``` to be more explicit
I see this as "communicating in general is just a way to make a memory of something (like a sentence) and transmitting it to another being". I understand it's unusual, but if the memory module works well, it could mean opening agent communication without building other complex modules. I'm very open to discussion, so please tell me if you have any suggestions regarding this way of doing things !

##### A couple of examples of the structure of the new memory


```python

# Observation from environment
MemoryItem(
    entry_content="The space next to me looks crowded",
    entry_type = "coordinates",
    entry_step = 43,
    metadata={
        "conversation_id": "conv_789",
        "current_loc": agent.pos,
    }
)

# coordinates transfered from another agent
MemoryItem(
    entry_content= (1,3),
    entry_type = "coordinates",
    entry_step = 43,
    metadata={
        "external_agent_id" : external.id,
    }
)


```



## Example usage

```python
# Creating a memory for an agent
agent.memory = Memory(model=self.model, stm_capacity=10)

# Storing information
entry_content= "The space next to me looks crowded",
entry_type = "coordinates",
entry_step = 43,
entry_metadata={
    "conversation_id": "conv_789",
    "current_loc": agent.pos,
}

entry = agent.memory.remember_short_term(
    model,
    entry_content,
    entry_type,
    entry_step,
    entry_metadata
)

# Recalling information
position_data = agent.memory.recall(position_entry_id)

# Finding entries by type in the short term memory
all_position_entries = agent.memory.get_by_type_st("position", include_short_term = True, include_long_term = False,)

# Sharing memory with another agent
agent.memory.tell_to(position_id, external_agent)

# Removing an entry
agent.memory.forget(position_entry_id)
```

## What I want to do next 


- I would like to transform get_by_entry_type into a more general ```search()``` method looking like this :

```python
def search(self, query: str = None, entry_type: List[str] = None, 
            limit: int = 5) -> List[Tuple[MemoryEntry]]:
    """
    Search in short-term memory.
    Implementation could return the n-first entries with relevance scores based on :
        - Exact search
        - Substring search
        - Regex

    Useful for LLM-based agents, but not only. 
    I would 
    """
    return
```

- Mabe serialization methods could also be useful directly in short term and long term memory (```from_dict()```, ```to_dict()```)