from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from datetime import datetime


class AgentState(TypedDict):
    """State shared across all agents"""

    # Conversation
    messages: Annotated[List[BaseMessage], add_messages]

    # Current context
    current_task: str
    user_query: str

    # Memory context
    relevant_memories: List[Dict[str, Any]]
    episodic_context: str
    semantic_context: str

    # Agent routing
    next_agent: str
    agent_history: List[str]

    # Task results
    email_results: Optional[Dict[str, Any]]
    calendar_results: Optional[Dict[str, Any]]
    idea_results: Optional[Dict[str, Any]]

    # Metadata
    timestamp: datetime
    user_id: str
    session_id: str

    # Error handling
    errors: List[str]
    retry_count: int
