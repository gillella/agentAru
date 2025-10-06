from typing import Dict, Any, List
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import logging

from src.core.state import AgentState
from src.core.model_manager import ModelManager
from src.memory.memory_manager import AgentMemoryManager

logger = logging.getLogger(__name__)


class EmailAgent:
    """Specialized agent for email operations"""

    def __init__(self, model_manager: ModelManager, memory_manager: AgentMemoryManager):
        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.llm = model_manager.get_model()

    def process(self, state: AgentState) -> AgentState:
        """Process email-related tasks"""

        try:
            user_query = state["user_query"]

            # Get user's email preferences from memory
            email_prefs = self.memory_manager.search_memories(
                query="email preferences writing style", memory_type="semantic", limit=3
            )

            # Build context
            context = self._build_email_context(user_query, email_prefs)

            # For now, simple response (tools will be added later)
            response = self.llm.invoke(
                [SystemMessage(content=context), *state["messages"]]
            )

            # Update state
            state["email_results"] = {"status": "processed", "message": response.content}
            state["agent_history"].append("email_agent")
            state["messages"].append(AIMessage(content=response.content))
            state["next_agent"] = ""  # Return to supervisor

            logger.info("Email agent processed successfully")
            return state

        except Exception as e:
            logger.error(f"Email agent processing failed: {e}")
            state["errors"].append(f"Email agent error: {str(e)}")
            state["next_agent"] = ""
            return state

    def _build_email_context(self, query: str, preferences: List[Dict]) -> str:
        pref_text = "\n".join([p.get("memory", "") for p in preferences])

        return f"""You are AgentAru's email specialist.

User Preferences:
{pref_text if pref_text else "No specific preferences stored yet."}

Your capabilities:
- Read and categorize emails
- Draft replies in the user's style
- Send emails
- Organize inbox

Current request: {query}

Provide a helpful response about the email task."""
