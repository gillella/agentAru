from typing import Dict, Any
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging

from src.core.state import AgentState
from src.core.model_manager import ModelManager
from src.memory.memory_manager import AgentMemoryManager

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Orchestrates and routes to specialized agents"""

    def __init__(self, model_manager: ModelManager, memory_manager: AgentMemoryManager):
        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.llm = model_manager.get_model()

        # Create supervisor prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_prompt()),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="memory_context"),
                (
                    "human",
                    "Based on the conversation, which agent should handle this? Or should we end?",
                ),
            ]
        )

        self.chain = self.prompt | self.llm

    def _get_system_prompt(self) -> str:
        return """You are AgentAru's supervisor agent. Your role is to:

1. Analyze user requests and determine which specialized agent should handle them
2. Consider relevant memories and past context
3. Coordinate between multiple agents if needed
4. Decide when the task is complete

Available Agents:
- email_agent: Handles reading, categorizing, drafting, and sending emails
- calendar_agent: Manages calendar, schedules meetings, checks availability
- idea_agent: Captures ideas, notes, organizes thoughts

Decision Rules:
- If the query is about emails (read, draft, send, organize) → email_agent
- If about calendar/scheduling/meetings → calendar_agent
- If about saving ideas, notes, brainstorming → idea_agent
- If task is complete or query is general chat → end
- If uncertain, ask for clarification

Consider user's past preferences from memory when making decisions.

Respond with ONLY the agent name or 'end', nothing else."""

    def process(self, state: AgentState) -> AgentState:
        """Process state and route to appropriate agent"""

        try:
            # Get relevant memories
            user_query = state["user_query"]
            memories = self.memory_manager.search_memories(query=user_query, limit=3)

            # Build memory context
            memory_context = []
            if memories:
                memory_text = "\n".join([f"- {m.get('memory', '')}" for m in memories])
                memory_context = [
                    SystemMessage(content=f"Relevant past context:\n{memory_text}")
                ]

            # Get decision from LLM
            response = self.chain.invoke(
                {"messages": state["messages"], "memory_context": memory_context}
            )

            # Parse decision
            decision = response.content.strip().lower()

            # Validate decision
            valid_agents = ["email_agent", "calendar_agent", "idea_agent", "end"]
            if decision not in valid_agents:
                logger.warning(f"Invalid routing decision: {decision}, defaulting to 'end'")
                decision = "end"

            # Update state
            state["next_agent"] = decision
            state["agent_history"].append("supervisor")
            state["relevant_memories"] = memories

            # Add supervisor message to conversation
            state["messages"].append(AIMessage(content=f"Routing to: {decision}"))

            logger.info(f"Supervisor routed to: {decision}")
            return state

        except Exception as e:
            logger.error(f"Supervisor processing failed: {e}")
            state["errors"].append(f"Supervisor error: {str(e)}")
            state["next_agent"] = "end"
            return state
