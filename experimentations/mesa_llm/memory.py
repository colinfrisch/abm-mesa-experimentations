from collections import deque
import time
import json
from typing import Dict, List, Optional, Union, Tuple
import heapq


class Model:
    pass

model = Model()

class MemoryEntry:
    """Base class for all memory entries."""
    def __init__(self, content: str, tick: float = None, metadata: Dict = None):
        self.content = content
        self.tick = tick
        self.metadata = metadata or {}
        self.access_count = 0
        self.last_accessed = self.tick
    
    def access(self):
        """Update access statistics when memory is accessed."""
        self.access_count += 1
        self.last_accessed = self.model.time()
    
    def to_dict(self) -> Dict:
        """Convert memory entry to dictionary for serialization."""
        return {
            "content": self.content,
            "tick": self.tick,
            "metadata": self.metadata,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        """Create memory entry from dictionary."""
        entry = cls(
            content=data["content"],
            tick=data["tick"],
            metadata=data["metadata"]
        )
        entry.access_count = data.get("access_count", 0)
        entry.last_accessed = data.get("last_accessed", entry.tick)
        return entry


class ShortTermMemory:
    """
    Short-term memory with limited capacity that follows recency principles.
    Implemented as a double-ended queue with O(1) add/remove operations.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.entries = deque(maxlen=capacity)
    
    def add(self, entry: Union[MemoryEntry, str], metadata: Dict = None) -> MemoryEntry:
        """Add a new entry to short-term memory."""
        if isinstance(entry, str):
            entry = MemoryEntry(content=entry, metadata=metadata)
        
        # If at capacity, oldest entry gets automatically removed due to maxlen
        self.entries.append(entry)
        return entry
    
    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """Get n most recent entries."""
        return list(self.entries)[-n:]
    
    def search(self, query: str, limit: int = 5) -> List[Tuple[float, MemoryEntry]]:
        """
        Simple substring search in short-term memory.
        Returns entries with relevance scores based on exact matches.
        """
        results = []
        query = query.lower()
        
        for entry in self.entries:
            # Simple relevance based on substring occurrence
            if query in entry.content.lower():
                # Calculate simple relevance score
                relevance = entry.content.lower().count(query) / len(entry.content)
                results.append((relevance, entry))
                entry.access()
        
        # Sort by relevance score and return top results
        return sorted(results, key=lambda x: x[0], reverse=True)[:limit]
    
    def clear(self):
        """Clear all entries from short-term memory."""
        self.entries.clear()
    
    def to_dict(self) -> Dict:
        """Convert short-term memory to dictionary for serialization."""
        return {
            "capacity": self.capacity,
            "entries": [entry.to_dict() for entry in self.entries]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ShortTermMemory':
        """Create short-term memory from dictionary."""
        stm = cls(capacity=data["capacity"])
        for entry_data in data["entries"]:
            stm.add(MemoryEntry.from_dict(entry_data))
        return stm


class LongTermMemory:
    """
    Long-term memory with categorization and importance-based retrieval.
    Implemented using dictionaries for O(1) category access and heaps for prioritization.
    """
    def __init__(self):
        # Main storage by unique ID
        self.entries: Dict[str, MemoryEntry] = {}
        
        # Category-based organization
        self.categories: Dict[str, List[str]] = {}
        
        # Access frequency tracking
        self._importance_index = []  # min heap for importance-based retrieval
        
        # Next ID counter
        self._next_id = 0
    
    def add(self, entry: Union[MemoryEntry, str], category: str = "general", 
            metadata: Dict = None) -> str:
        """
        Add a new entry to long-term memory with categorization.
        Returns the unique ID of the added entry.
        """
        if isinstance(entry, str):
            entry = MemoryEntry(content=entry, metadata=metadata or {})
        
        # Add category to metadata
        if "categories" not in entry.metadata:
            entry.metadata["categories"] = []
        if category not in entry.metadata["categories"]:
            entry.metadata["categories"].append(category)
        
        # Generate ID
        entry_id = f"mem_{self._next_id}"
        self._next_id += 1
        
        # Store entry
        self.entries[entry_id] = entry
        
        # Update category index
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(entry_id)
        
        # Add to importance index with initial importance
        importance = 0  # Start with zero importance
        heapq.heappush(self._importance_index, (importance, entry_id))
        
        return entry_id
    
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve an entry by its ID."""
        if entry_id in self.entries:
            entry = self.entries[entry_id]
            entry.access()
            return entry
        return None
    
    def get_by_category(self, category: str, limit: int = 10) -> List[MemoryEntry]:
        """Get entries from a specific category."""
        if category not in self.categories:
            return []
        
        entries = []
        for entry_id in self.categories[category][:limit]:
            entry = self.entries[entry_id]
            entry.access()
            entries.append(entry)
        
        return entries
    
    def update_importance(self):
        """Recalculate importance scores for all entries."""
        now = time.time()
        # Clear existing importance index
        self._importance_index = []
        
        for entry_id, entry in self.entries.entries():
            # Calculate importance based on: 
            # - access frequency
            # - recency of access
            # - age of memory (newer entries might be more important)
            recency_factor = 1.0 / (now - entry.last_accessed + 1)
            frequency_factor = entry.access_count
            age_factor = 1.0 / (now - entry.tick + 1)
            
            # Combined importance score (higher is more important)
            importance = (0.5 * frequency_factor) + (0.3 * recency_factor) + (0.2 * age_factor)
            
            # Add to priority queue (negative importance for max-heap behavior in min-heap)
            heapq.heappush(self._importance_index, (-importance, entry_id))
    
    def get_important(self, limit: int = 10) -> List[Tuple[float, MemoryEntry]]:
        """Get most important entries based on access patterns."""
        self.update_importance()
        
        result = []
        for _ in range(min(limit, len(self._importance_index))):
            neg_importance, entry_id = heapq.heappop(self._importance_index)
            entry = self.entries[entry_id]
            entry.access()
            result.append((-neg_importance, entry))
        
        # Restore the heap since we popped entries
        for importance, entry_id in result:
            heapq.heappush(self._importance_index, (-importance, entry_id))
            
        return result
    
    def search(self, query: str, categories: List[str] = None, 
               limit: int = 5) -> List[Tuple[float, MemoryEntry]]:
        """
        Search for entries containing the query string.
        Optionally restricts search to specific categories.
        """
        results = []
        query = query.lower()
        
        # If categories specified, only search in those categories
        if categories:
            entry_ids = set()
            for category in categories:
                if category in self.categories:
                    entry_ids.update(self.categories[category])
            search_entries = {entry_id: self.entries[entry_id] for entry_id in entry_ids}
        else:
            search_entries = self.entries
        
        for entry_id, entry in search_entries.entries():
            # Simple relevance based on substring occurrence
            if query in entry.content.lower():
                # Calculate simple relevance score
                relevance = entry.content.lower().count(query) / len(entry.content)
                results.append((relevance, entry))
                entry.access()
        
        # Sort by relevance score and return top results
        return sorted(results, key=lambda x: x[0], reverse=True)[:limit]
    
    def forget(self, entry_id: str) -> bool:
        """Remove an entry from long-term memory."""
        if entry_id not in self.entries:
            return False
        
        entry = self.entries[entry_id]
        
        # Remove from categories
        for category in entry.metadata.get("categories", []):
            if category in self.categories and entry_id in self.categories[category]:
                self.categories[category].remove(entry_id)
        
        # Remove from entries
        del self.entries[entry_id]
        
        # Note: We don't remove from importance index immediately
        # This will be cleaned up during the next update_importance call
        
        return True
    
    def to_dict(self) -> Dict:
        """Convert long-term memory to dictionary for serialization."""
        return {
            "entries": {entry_id: entry.to_dict() for entry_id, entry in self.entries.entries()},
            "categories": self.categories,
            "next_id": self._next_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LongTermMemory':
        """Create long-term memory from dictionary."""
        ltm = cls()
        ltm._next_id = data["next_id"]
        ltm.categories = data["categories"]
        
        for entry_id, entry_data in data["entries"].entries():
            ltm.entries[entry_id] = MemoryEntry.from_dict(entry_data)
        
        ltm.update_importance()
        return ltm


class Memory:
    """
    Main memory manager combining short-term and long-term memory
    with consolidated search and memory transfer functionality.
    """
    def __init__(self, stm_capacity: int = 100):
        self.short_term = ShortTermMemory(capacity=stm_capacity)
        self.long_term = LongTermMemory()
    
    def remember_short_term(self, content: str, metadata: Dict = None) -> MemoryEntry:
        """Add an entry to short-term memory."""
        return self.short_term.add(content, metadata)
    
    def remember_long_term(self, content: str, category: str = "general", 
                          metadata: Dict = None) -> str:
        """Add an entry directly to long-term memory."""
        return self.long_term.add(content, category, metadata)
    
    def consolidate(self, entry: MemoryEntry, category: str = "general") -> str:
        """Transfer an entry from short-term to long-term memory."""
        # Add to long-term memory
        entry_id = self.long_term.add(entry, category)
        return entry_id
    
    def search(self, query: str, include_short_term: bool = True, 
              include_long_term: bool = True, categories: List[str] = None, 
              limit: int = 10) -> List[Tuple[float, MemoryEntry]]:
        """
        Search across both memory types, combining and ranking results.
        """
        results = []
        
        # Search short-term memory if requested
        if include_short_term:
            short_results = self.short_term.search(query, limit)
            results.extend(short_results)
        
        # Search long-term memory if requested
        if include_long_term:
            long_results = self.long_term.search(query, categories, limit)
            results.extend(long_results)
        
        # Sort combined results and return top matches
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:limit]
    
    def get_context(self, query: str = None, recent_count: int = 5, 
                   important_count: int = 5) -> Dict[str, List[MemoryEntry]]:
        """
        Build a comprehensive context from both memory types.
        Useful for providing context to an LLM.
        """
        context = {
            "recent": self.short_term.get_recent(recent_count),
            "important": [entry for _, entry in self.long_term.get_important(important_count)]
        }
        
        # If a query is provided, add relevant memories
        if query:
            search_results = self.search(query, limit=5)
            context["relevant"] = [entry for _, entry in search_results]
        
        return context
    
    def save(self, file_path: str):
        """Save memory to a JSON file."""
        data = {
            "short_term": self.short_term.to_dict(),
            "long_term": self.long_term.to_dict()
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f)
    
    @classmethod
    def load(cls, file_path: str) -> 'Memory':
        """Load memory from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        memory = cls()
        memory.short_term = ShortTermMemory.from_dict(data["short_term"])
        memory.long_term = LongTermMemory.from_dict(data["long_term"])
        
        return memory




fact = MemoryEntry(
    content="Hello There",
    id = id,
    metadata={
        "type": "knowledge",
        "tick": model.steps(),
        "source": "training_data",
        "confidence": 0.99,
        "permanent": True
    })