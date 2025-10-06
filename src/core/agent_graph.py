from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from datetime import datetime
import logging

from src.core.state import AgentState
from src.core.model_manager import ModelManager
from src.memory.memory_manager import AgentMemoryManager

logger = logging.getLogger(__name__)


class AgentAruGraph:
    """Main LangGraph orchestrator for AgentAru"""

    def __init__(
        self,
        model_manager: ModelManager,
        memory_manager: AgentMemoryManager,
        user_id: str = "default_user",
    ):
        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.user_id = user_id

        # Initialize agents (will be imported later)
        self.supervisor = None
        self.email_agent = None
        self.calendar_agent = None
        self.idea_agent = None

        # Build graph
        self.graph = self._build_graph()
        self.app = None

    def _build_graph(self) -> StateGraph:
        """Construct the agent workflow graph"""

        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("email_agent", self.email_node)
        workflow.add_node("calendar_agent", self.calendar_node)
        workflow.add_node("idea_agent", self.idea_node)
        workflow.add_node("memory_update", self.memory_update_node)

        # Define edges
        workflow.set_entry_point("supervisor")

        # Conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self.route_to_agent,
            {
                "email_agent": "email_agent",
                "calendar_agent": "calendar_agent",
                "idea_agent": "idea_agent",
                "end": "memory_update",
            },
        )

        # Return to supervisor after each agent
        workflow.add_edge("email_agent", "supervisor")
        workflow.add_edge("calendar_agent", "supervisor")
        workflow.add_edge("idea_agent", "supervisor")

        # End after memory update
        workflow.add_edge("memory_update", END)

        logger.info("Built agent graph with 5 nodes")
        return workflow

    def supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor decision-making node"""
        if self.supervisor:
            return self.supervisor.process(state)
        else:
            # Placeholder for now
            logger.warning("Supervisor agent not initialized")
            state["next_agent"] = "end"
            return state

    def email_node(self, state: AgentState) -> AgentState:
        """Email agent processing"""
        if self.email_agent:
            return self.email_agent.process(state)
        else:
            logger.warning("Email agent not initialized")
            state["next_agent"] = ""
            return state

    def calendar_node(self, state: AgentState) -> AgentState:
        """Calendar agent processing"""
        if self.calendar_agent:
            return self.calendar_agent.process(state)
        else:
            logger.warning("Calendar agent not initialized")
            state["next_agent"] = ""
            return state

    def idea_node(self, state: AgentState) -> AgentState:
        """Idea capture agent processing"""
        if self.idea_agent:
            return self.idea_agent.process(state)
        else:
            logger.warning("Idea agent not initialized")
            state["next_agent"] = ""
            return state

    def memory_update_node(self, state: AgentState) -> AgentState:
        """Update long-term memory"""

        try:
            # Store interaction
            self.memory_manager.add_interaction(
                messages=state["messages"],
                metadata={
                    "task": state.get("current_task"),
                    "agents_used": state.get("agent_history", []),
                },
            )
            logger.info(f"Updated memory for session: {state.get('session_id')}")
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            state["errors"].append(f"Memory update failed: {str(e)}")

        return state

    def route_to_agent(self, state: AgentState) -> str:
        """Determine which agent to call next"""
        next_agent = state.get("next_agent", "end")
        logger.debug(f"Routing to: {next_agent}")
        return next_agent

    def compile(self, checkpointer=None):
        """Compile the graph for execution"""
        if checkpointer is None:
            checkpointer = MemorySaver()

        self.app = self.graph.compile(checkpointer=checkpointer)
        logger.info("Compiled agent graph")
        return self.app

    async def arun(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Run the agent asynchronously"""

        if not self.app:
            self.compile()

        # Prepare initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_input)],
            "current_task": "",
            "user_query": user_input,
            "relevant_memories": [],
            "episodic_context": "",
            "semantic_context": "",
            "next_agent": "",
            "agent_history": [],
            "email_results": None,
            "calendar_results": None,
            "idea_results": None,
            "timestamp": datetime.now(),
            "user_id": self.user_id,
            "session_id": session_id or f"session_{datetime.now().timestamp()}",
            "errors": [],
            "retry_count": 0,
        }

        # Execute graph
        config = {"configurable": {"thread_id": session_id or "default"}}

        try:
            final_state = await self.app.ainvoke(initial_state, config=config)
            logger.info(f"Async execution completed for session: {session_id}")
            return final_state
        except Exception as e:
            logger.error(f"Async execution failed: {e}")
            raise

    def run(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Run the agent synchronously"""

        if not self.app:
            self.compile()

        # Prepare initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_input)],
            "current_task": "",
            "user_query": user_input,
            "relevant_memories": [],
            "episodic_context": "",
            "semantic_context": "",
            "next_agent": "",
            "agent_history": [],
            "email_results": None,
            "calendar_results": None,
            "idea_results": None,
            "timestamp": datetime.now(),
            "user_id": self.user_id,
            "session_id": session_id or f"session_{datetime.now().timestamp()}",
            "errors": [],
            "retry_count": 0,
        }

        config = {"configurable": {"thread_id": session_id or "default"}}

        try:
            final_state = self.app.invoke(initial_state, config=config)
            logger.info(f"Sync execution completed for session: {session_id}")
            return final_state
        except Exception as e:
            logger.error(f"Sync execution failed: {e}")
            raise

    def set_agents(self, supervisor=None, email=None, calendar=None, idea=None):
        """Set agent instances"""
        if supervisor:
            self.supervisor = supervisor
        if email:
            self.email_agent = email
        if calendar:
            self.calendar_agent = calendar
        if idea:
            self.idea_agent = idea
        logger.info("Updated agent instances")
