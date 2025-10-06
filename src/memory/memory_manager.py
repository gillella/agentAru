from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import logging
import os

logger = logging.getLogger(__name__)


class AgentMemoryManager:
    """Long-term memory system with decay and retrieval"""

    def __init__(
        self, user_id: str = "default_user", api_key: str = None, config: Dict[str, Any] = None
    ):
        self.user_id = user_id
        self.config = config or {}

        # Initialize Mem0 with local embeddings
        try:
            # Configure Mem0 to use Ollama for embeddings AND LLM (fully local, no API key needed)
            memory_config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "path": os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/vector_db"),
                        "collection_name": "agentaru_memories",
                        "embedding_model_dims": 768  # Nomic-embed-text dimension
                    }
                },
                "llm": {
                    "provider": "ollama",
                    "config": {
                        "model": "qwen2.5:7b-instruct",
                        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                    }
                },
                "embedder": {
                    "provider": "ollama",
                    "config": {
                        "model": "nomic-embed-text:latest",
                        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                    }
                },
                "version": "v1.1"
            }

            self.memory = Memory.from_config(memory_config)
            logger.info(f"Initialized memory for user: {user_id} (using local Ollama embeddings)")
        except Exception as e:
            logger.warning(f"Failed to initialize Mem0 with Ollama embeddings: {e}")
            logger.info("Falling back to simple in-memory storage")
            self.memory = None

        # Memory decay settings
        self.decay_days = self.config.get("decay_days", 90)
        self.relevance_threshold = self.config.get("relevance_threshold", 0.3)

    def add_interaction(
        self, messages: List[BaseMessage], metadata: Dict[str, Any] = None
    ) -> str:
        """Store conversation interaction"""

        if not self.memory:
            logger.debug("Memory system not available, skipping interaction storage")
            return ""

        # Convert messages to Mem0 format
        formatted_messages = self._format_messages(messages)

        # Add metadata
        memory_metadata = {
            "timestamp": datetime.now().isoformat(),
            "type": "episodic",
            **(metadata or {}),
        }

        # Store in Mem0
        try:
            result = self.memory.add(
                messages=formatted_messages, user_id=self.user_id, metadata=memory_metadata
            )
            logger.debug(f"Added episodic memory: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to add interaction memory: {e}")
            return ""

    def add_fact(
        self, fact: str, category: str = "general", metadata: Dict[str, Any] = None
    ) -> str:
        """Store semantic knowledge"""

        memory_metadata = {
            "type": "semantic",
            "category": category,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }

        try:
            result = self.memory.add(
                messages=[{"role": "system", "content": fact}],
                user_id=self.user_id,
                metadata=memory_metadata,
            )
            logger.debug(f"Added semantic memory: {category}/{fact[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Failed to add fact memory: {e}")
            return ""

    def add_procedure(
        self, task: str, steps: List[str], metadata: Dict[str, Any] = None
    ) -> str:
        """Store procedural knowledge (how-to)"""

        procedure_content = f"Task: {task}\nSteps:\n" + "\n".join(
            f"{i+1}. {step}" for i, step in enumerate(steps)
        )

        memory_metadata = {
            "type": "procedural",
            "task": task,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }

        try:
            result = self.memory.add(
                messages=[{"role": "system", "content": procedure_content}],
                user_id=self.user_id,
                metadata=memory_metadata,
            )
            logger.debug(f"Added procedural memory: {task}")
            return result
        except Exception as e:
            logger.error(f"Failed to add procedure memory: {e}")
            return ""

    def search_memories(
        self,
        query: str,
        memory_type: str = None,
        limit: int = 5,
        apply_decay: bool = True,
    ) -> List[Dict[str, Any]]:
        """Search relevant memories with optional decay"""

        if not self.memory:
            logger.debug("Memory system not available, returning empty results")
            return []

        try:
            # Search with Mem0
            results = self.memory.search(
                query=query, user_id=self.user_id, limit=limit * 2  # Get more for filtering
            )

            # Convert to list if needed
            if not isinstance(results, list):
                results = [results] if results else []

            # Filter by type if specified
            if memory_type:
                results = [
                    r for r in results if r.get("metadata", {}).get("type") == memory_type
                ]

            # Apply temporal decay
            if apply_decay:
                results = self._apply_decay(results)

            # Sort by relevance score and limit
            results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)[:limit]

            logger.debug(f"Found {len(results)} memories for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []

    def _apply_decay(self, memories: List[Dict]) -> List[Dict]:
        """Apply temporal decay to memory scores"""
        now = datetime.now()
        decayed_memories = []

        for memory in memories:
            timestamp_str = memory.get("metadata", {}).get("timestamp")
            if not timestamp_str:
                decayed_memories.append(memory)
                continue

            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                days_old = (now - timestamp).days

                # Exponential decay formula
                decay_factor = max(0.1, 1 - (days_old / self.decay_days))

                # Apply decay to score
                original_score = memory.get("score", 1.0)
                memory["score"] = original_score * decay_factor
                memory["decay_factor"] = decay_factor

                # Only keep if above threshold
                if memory["score"] >= self.relevance_threshold:
                    decayed_memories.append(memory)
            except Exception as e:
                logger.warning(f"Failed to apply decay to memory: {e}")
                decayed_memories.append(memory)

        return decayed_memories

    def get_context_for_query(self, query: str, max_tokens: int = 2000) -> str:
        """Get relevant memory context for a query"""

        memories = self.search_memories(query, limit=10)

        context_parts = []
        token_count = 0

        for memory in memories:
            memory_text = memory.get("memory", "")
            # Rough token estimation (4 chars ≈ 1 token)
            estimated_tokens = len(memory_text) // 4

            if token_count + estimated_tokens > max_tokens:
                break

            context_parts.append(memory_text)
            token_count += estimated_tokens

        return "\n\n".join(context_parts)

    def _format_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain messages to Mem0 format"""
        formatted = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            else:
                role = "system"

            formatted.append({"role": role, "content": msg.content})

        return formatted

    def update_memory(self, memory_id: str, updates: Dict[str, Any]):
        """Update existing memory"""
        try:
            return self.memory.update(memory_id=memory_id, data=updates)
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return None

    def delete_memory(self, memory_id: str):
        """Delete specific memory"""
        try:
            return self.memory.delete(memory_id=memory_id)
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return None

    def get_all_memories(self, memory_type: str = None) -> List[Dict[str, Any]]:
        """Retrieve all memories for user"""
        try:
            all_memories = self.memory.get_all(user_id=self.user_id)

            if memory_type:
                return [
                    m
                    for m in all_memories
                    if m.get("metadata", {}).get("type") == memory_type
                ]

            return all_memories
        except Exception as e:
            logger.error(f"Failed to get all memories: {e}")
            return []

    def export_memories(self, filepath: str):
        """Export memories to JSON file"""
        import json

        try:
            memories = self.get_all_memories()
            with open(filepath, "w") as f:
                json.dump(memories, f, indent=2, default=str)
            logger.info(f"Exported {len(memories)} memories to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export memories: {e}")

    def import_memories(self, filepath: str):
        """Import memories from JSON file"""
        import json

        try:
            with open(filepath, "r") as f:
                memories = json.load(f)

            for memory in memories:
                self.memory.add(
                    messages=[{"role": "system", "content": memory.get("memory", "")}],
                    user_id=self.user_id,
                    metadata=memory.get("metadata", {}),
                )

            logger.info(f"Imported {len(memories)} memories from {filepath}")
        except Exception as e:
            logger.error(f"Failed to import memories: {e}")
