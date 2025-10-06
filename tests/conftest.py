import pytest
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.model_manager import ModelManager
from src.memory.memory_manager import AgentMemoryManager


@pytest.fixture
def mock_model_manager():
    """Mock model manager"""
    manager = Mock(spec=ModelManager)
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Test response")
    manager.get_model.return_value = mock_llm
    return manager


@pytest.fixture
def mock_memory_manager():
    """Mock memory manager"""
    manager = Mock(spec=AgentMemoryManager)
    manager.search_memories.return_value = []
    manager.add_interaction.return_value = "test_id"
    manager.add_fact.return_value = "fact_id"
    return manager


@pytest.fixture
def sample_state():
    """Sample agent state for testing"""
    from src.core.state import AgentState
    from langchain_core.messages import HumanMessage
    from datetime import datetime

    return {
        "messages": [HumanMessage(content="Test query")],
        "current_task": "test",
        "user_query": "Test query",
        "relevant_memories": [],
        "episodic_context": "",
        "semantic_context": "",
        "next_agent": "",
        "agent_history": [],
        "email_results": None,
        "calendar_results": None,
        "idea_results": None,
        "timestamp": datetime.now(),
        "user_id": "test_user",
        "session_id": "test_session",
        "errors": [],
        "retry_count": 0,
    }
