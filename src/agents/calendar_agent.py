from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage
import logging

from src.core.state import AgentState
from src.core.model_manager import ModelManager
from src.memory.memory_manager import AgentMemoryManager

logger = logging.getLogger(__name__)


class CalendarAgent:
    """Specialized agent for calendar operations"""

    def __init__(self, model_manager: ModelManager, memory_manager: AgentMemoryManager):
        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.llm = model_manager.get_model()

    def process(self, state: AgentState) -> AgentState:
        """Process calendar-related tasks"""

        try:
            user_query = state["user_query"]

            # Get calendar preferences from memory
            calendar_prefs = self.memory_manager.search_memories(
                query="calendar meeting preferences", memory_type="semantic", limit=3
            )

            # Build context
            context = self._build_calendar_context(user_query, calendar_prefs)

            # Process with LLM
            response = self.llm.invoke(
                [SystemMessage(content=context), *state["messages"]]
            )

            # Update state
            state["calendar_results"] = {
                "status": "processed",
                "message": response.content,
            }
            state["agent_history"].append("calendar_agent")
            state["messages"].append(AIMessage(content=response.content))
            state["next_agent"] = ""  # Return to supervisor

            logger.info("Calendar agent processed successfully")
            return state

        except Exception as e:
            logger.error(f"Calendar agent processing failed: {e}")
            state["errors"].append(f"Calendar agent error: {str(e)}")
            state["next_agent"] = ""
            return state

    def _build_calendar_context(self, query: str, preferences) -> str:
        pref_text = "\n".join([p.get("memory", "") for p in preferences])

        return f"""You are AgentAru's calendar specialist.

User Preferences:
{pref_text if pref_text else "No specific preferences stored yet."}

Your capabilities:
- Schedule meetings
- Check availability
- Manage events
- Set reminders

Current request: {query}

Provide a helpful response about the calendar task."""
