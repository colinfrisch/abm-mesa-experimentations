from memory_V2 import MemoryItem

external = 1
recipient = 1





# coordinates storage
conversation = MemoryItem(
    content= (1,3),
    metadata={
        "type": "coordinates",
        "step": 76,
        "speaker": "user",
    }
)

# Health information transfer from another agent
agent_response = MemoryItem(
    content= 76,
    metadata={
        "external_agent_id" : external.id,
        "type": "health",
        "step": 110,
    }
)

# Observation from environment
observation = MemoryItem(
    content="The space next to me looks crowded",
    metadata={
        "type": "discussion",
        "step": 20,
        "conversation_id": "conv_789",
        "recipient": recipient.id,
    }
)
