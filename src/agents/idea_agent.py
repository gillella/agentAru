from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage
import logging

from src.core.state import AgentState
from src.core.model_manager import ModelManager
from src.memory.memory_manager import AgentMemoryManager

logger = logging.getLogger(__name__)


class IdeaAgent:
    """Specialized agent for capturing and organizing ideas"""

    def __init__(self, model_manager: ModelManager, memory_manager: AgentMemoryManager):
        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.llm = model_manager.get_model()

    def process(self, state: AgentState) -> AgentState:
        """Process idea capture and organization tasks"""

        try:
            user_query = state["user_query"]

            # Get related ideas from memory
            related_ideas = self.memory_manager.search_memories(
                query=user_query, memory_type="semantic", limit=5
            )

            # Build context
            context = self._build_idea_context(user_query, related_ideas)

            # Process with LLM
            response = self.llm.invoke(
                [SystemMessage(content=context), *state["messages"]]
            )

            # Store new idea if it's a capture request
            if "capture" in user_query.lower() or "save" in user_query.lower():
                self.memory_manager.add_fact(
                    fact=user_query, category="idea", metadata={"type": "user_idea"}
                )

            # Update state
            state["idea_results"] = {"status": "processed", "message": response.content}
            state["agent_history"].append("idea_agent")
            state["messages"].append(AIMessage(content=response.content))
            state["next_agent"] = ""  # Return to supervisor

            logger.info("Idea agent processed successfully")
            return state

        except Exception as e:
            logger.error(f"Idea agent processing failed: {e}")
            state["errors"].append(f"Idea agent error: {str(e)}")
            state["next_agent"] = ""
            return state

    def _build_idea_context(self, query: str, related_ideas) -> str:
        ideas_text = "\n".join([f"- {idea.get('memory', '')}" for idea in related_ideas])

        return f"""You are AgentAru's idea management specialist.

Related Ideas:
{ideas_text if ideas_text else "No related ideas found."}

Your capabilities:
- Capture new ideas and notes
- Organize thoughts by category
- Link related concepts
- Retrieve past ideas

Current request: {query}

Provide a helpful response about the idea task."""
