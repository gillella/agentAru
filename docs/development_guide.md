# AgentAru Development Guide

## Getting Started

### Development Setup

```bash
# Clone and setup
git clone <repo-url>
cd agentaru
bash scripts/setup.sh

# Activate virtual environment
source .venv/bin/activate

# Install dev dependencies
pip install pytest black ruff mypy

# Setup pre-commit hooks (optional)
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
black src/ tests/
ruff check src/ tests/
EOF
chmod +x .git/hooks/pre-commit
```

### Project Structure

```
agentaru/
├── src/                    # Source code
│   ├── agents/            # Specialized agents
│   ├── config/            # Configuration
│   ├── core/              # Core components
│   ├── integrations/      # External APIs
│   ├── memory/            # Memory system
│   ├── tools/             # LangChain tools
│   ├── ui/                # User interfaces
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── docs/                  # Documentation
├── data/                  # Local data storage
└── scripts/               # Utility scripts
```

## Core Concepts

### 1. Agent Development

#### Creating a New Agent

```python
# src/agents/my_agent.py

from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage
import logging

from src.core.state import AgentState
from src.core.model_manager import ModelManager
from src.memory.memory_manager import AgentMemoryManager

logger = logging.getLogger(__name__)


class MyAgent:
    """Description of what this agent does"""

    def __init__(
        self,
        model_manager: ModelManager,
        memory_manager: AgentMemoryManager
    ):
        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.llm = model_manager.get_model()

    def process(self, state: AgentState) -> AgentState:
        """Process the agent's task"""

        try:
            user_query = state["user_query"]

            # Get relevant memories
            memories = self.memory_manager.search_memories(
                query=user_query,
                memory_type="semantic",
                limit=5
            )

            # Build context
            context = self._build_context(user_query, memories)

            # Process with LLM
            response = self.llm.invoke([
                SystemMessage(content=context),
                *state["messages"]
            ])

            # Update state
            state["my_agent_results"] = {
                "status": "processed",
                "message": response.content
            }
            state["agent_history"].append("my_agent")
            state["messages"].append(AIMessage(content=response.content))
            state["next_agent"] = ""  # Return to supervisor

            logger.info("My agent processed successfully")
            return state

        except Exception as e:
            logger.error(f"My agent processing failed: {e}")
            state["errors"].append(f"My agent error: {str(e)}")
            state["next_agent"] = ""
            return state

    def _build_context(self, query: str, memories) -> str:
        memory_text = "\n".join([
            m.get("memory", "") for m in memories
        ])

        return f"""You are a specialized agent for [task].

Relevant Context:
{memory_text if memory_text else "No context available."}

Current request: {query}

Provide a helpful response."""
```

#### Registering the Agent

```python
# src/core/agent_graph.py

from src.agents.my_agent import MyAgent

class AgentAruGraph:
    def __init__(self, ...):
        # ... existing code ...
        self.my_agent = None

    def _build_graph(self):
        # Add node
        workflow.add_node("my_agent", self.my_agent_node)

        # Add routing
        workflow.add_conditional_edges(
            "supervisor",
            self.route_to_agent,
            {
                # ... existing routes ...
                "my_agent": "my_agent",
            }
        )

        # Return edge
        workflow.add_edge("my_agent", "supervisor")

    def my_agent_node(self, state):
        if self.my_agent:
            return self.my_agent.process(state)
        # ...

# In main.py or streamlit_app.py:
my_agent = MyAgent(model_manager, memory_manager)
graph.set_agents(..., my_agent=my_agent)
```

#### Update Supervisor Routing

```python
# src/agents/supervisor_agent.py

def _get_system_prompt(self):
    return """...

Available Agents:
- email_agent: ...
- calendar_agent: ...
- idea_agent: ...
- my_agent: Does [specific task]  # Add this

Decision Rules:
- If query is about [task] → my_agent  # Add this
...
"""
```

### 2. Tool Development

#### Creating LangChain Tools

```python
# src/tools/my_tools.py

from langchain.tools import tool
from typing import List, Dict, Any

@tool
def my_custom_tool(
    param1: str,
    param2: int = 10
) -> Dict[str, Any]:
    """
    Description of what the tool does.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Dictionary with results
    """
    try:
        # Implementation
        result = do_something(param1, param2)

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

#### Binding Tools to Agents

```python
# In your agent class

from src.tools.my_tools import my_custom_tool

class MyAgent:
    def __init__(self, model_manager, memory_manager):
        # ... existing code ...

        # Bind tools
        self.tools = [my_custom_tool]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def process(self, state):
        # Use LLM with tools
        response = self.llm_with_tools.invoke([...])

        # Process tool calls
        if response.tool_calls:
            for tool_call in response.tool_calls:
                result = self._execute_tool(tool_call)
                # Handle result

    def _execute_tool(self, tool_call):
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        for tool in self.tools:
            if tool.name == tool_name:
                return tool.invoke(tool_args)

        return {"error": f"Tool {tool_name} not found"}
```

### 3. Integration Development

#### Creating External Integrations

```python
# src/integrations/my_service.py

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MyServiceIntegration:
    """Integration with MyService API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with service"""
        try:
            # Authentication logic
            logger.info("Authenticated with MyService")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def get_data(self, query: str) -> List[Dict[str, Any]]:
        """Fetch data from service"""
        try:
            # API call
            response = self.client.get(query)
            return response.json()

        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return []

    def create_item(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create item in service"""
        try:
            # API call
            response = self.client.post(data)

            return {
                "status": "created",
                "id": response.json()["id"]
            }

        except Exception as e:
            logger.error(f"Failed to create item: {e}")
            return {"error": str(e)}
```

### 4. Memory System

#### Adding Custom Memory Types

```python
# In your agent or tool

# Add semantic fact
memory_manager.add_fact(
    fact="User prefers morning meetings",
    category="preferences",
    metadata={"source": "conversation"}
)

# Add procedural knowledge
memory_manager.add_procedure(
    task="Create project report",
    steps=[
        "Gather metrics",
        "Generate charts",
        "Write summary",
        "Export to PDF"
    ],
    metadata={"domain": "reporting"}
)

# Search with filters
memories = memory_manager.search_memories(
    query="meeting preferences",
    memory_type="semantic",
    limit=5,
    apply_decay=True
)
```

#### Custom Memory Retrieval

```python
# Advanced memory search with context
def get_enriched_context(query: str, user_id: str) -> str:
    # Recent episodic
    recent = memory_manager.search_memories(
        query=query,
        memory_type="episodic",
        limit=3
    )

    # Relevant semantic
    facts = memory_manager.search_memories(
        query=query,
        memory_type="semantic",
        limit=5
    )

    # Combine contexts
    context = f"""
Recent Conversations:
{format_memories(recent)}

Relevant Knowledge:
{format_memories(facts)}
"""

    return context
```

### 5. Model Configuration

#### Adding New Models

```yaml
# src/config/models.yaml

models:
  new_provider:
    - name: model-name
      display_name: "Model Display Name"
      context_window: 128000
      cost_per_1k_tokens:
        input: 0.001
        output: 0.002
      local: false
      capabilities: [chat, tool_use]
```

```python
# src/core/model_manager.py

def get_model(self, model_name, temperature=0.7, **kwargs):
    # ... existing code ...

    elif provider == "new_provider":
        from langchain_community.chat_models import ChatNewProvider

        model = ChatNewProvider(
            model=model_id,
            temperature=temperature,
            **kwargs
        )
```

## Testing

### Writing Unit Tests

```python
# tests/test_agents/test_my_agent.py

import pytest
from unittest.mock import Mock

from src.agents.my_agent import MyAgent


def test_agent_initialization(mock_model_manager, mock_memory_manager):
    """Test agent initializes correctly"""
    agent = MyAgent(mock_model_manager, mock_memory_manager)

    assert agent.model_manager == mock_model_manager
    assert agent.memory_manager == mock_memory_manager


def test_agent_processing(
    mock_model_manager,
    mock_memory_manager,
    sample_state
):
    """Test agent processes state correctly"""

    # Setup mocks
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Test response")
    mock_model_manager.get_model.return_value = mock_llm

    # Create agent
    agent = MyAgent(mock_model_manager, mock_memory_manager)

    # Process
    result = agent.process(sample_state)

    # Assertions
    assert result["next_agent"] == ""
    assert "my_agent" in result["agent_history"]
    assert result["my_agent_results"]["status"] == "processed"
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_agents/test_my_agent.py

# With coverage
pytest --cov=src tests/

# With output
pytest -v -s
```

### Integration Testing

```python
# tests/test_integrations/test_my_service.py

import pytest
from src.integrations.my_service import MyServiceIntegration


@pytest.mark.integration
def test_service_connection():
    """Test connection to actual service"""

    service = MyServiceIntegration(api_key="test-key")
    data = service.get_data("test query")

    assert isinstance(data, list)


# Run with: pytest -m integration
```

## Code Quality

### Formatting

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Linting

```bash
# Run ruff
ruff check src/ tests/

# Auto-fix
ruff check --fix src/ tests/
```

### Type Checking

```bash
# Run mypy
mypy src/
```

## Debugging

### Logging

```python
# Enable debug logging
import logging

logging.basicConfig(level=logging.DEBUG)

# Or in .env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Graph Visualization

```python
# Export graph structure
from langgraph.graph import StateGraph

graph = build_graph()
graph.get_graph().print_ascii()

# Or visualize
graph.get_graph().draw_png("graph.png")
```

### State Inspection

```python
# Add debug prints in nodes
def my_node(state):
    print(f"State at my_node: {state}")
    # ... process
    return state
```

## Best Practices

### 1. Error Handling

```python
def process(self, state):
    try:
        # Main logic
        result = do_something()

    except SpecificError as e:
        logger.error(f"Specific error: {e}")
        state["errors"].append(str(e))
        # Graceful degradation

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        state["errors"].append(f"Unexpected: {str(e)}")

    finally:
        # Cleanup
        pass

    return state
```

### 2. State Management

```python
# Always return modified state
def process(self, state):
    # Modify state
    state["field"] = value

    # Always return
    return state

# Don't mutate without returning
def bad_process(self, state):
    state["field"] = value
    # Missing return!
```

### 3. Memory Usage

```python
# Limit memory context
context = memory_manager.get_context_for_query(
    query=user_query,
    max_tokens=2000  # Control context size
)

# Regular cleanup
if days_since_start > 30:
    memory_manager.apply_decay()
```

### 4. Performance

```python
# Cache expensive operations
@lru_cache(maxsize=100)
def expensive_operation(param):
    # Cached result
    return result

# Batch operations
def process_batch(items):
    # Process together
    results = api.batch_call(items)
    return results
```

## Deployment

### Environment Setup

```bash
# Production .env
DEBUG=false
LOG_LEVEL=INFO
DEFAULT_MODEL=anthropic/claude-3-5-haiku-20241022  # Cost-effective
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY data/ data/

CMD ["streamlit", "run", "src/ui/streamlit_app.py"]
```

### Monitoring

```python
# Add metrics
from prometheus_client import Counter, Histogram

request_count = Counter('agent_requests', 'Agent requests')
response_time = Histogram('response_time', 'Response time')

def process(self, state):
    request_count.inc()

    with response_time.time():
        # Process
        pass
```

## Contributing

### Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes with tests
3. Run quality checks: `black . && ruff check . && pytest`
4. Commit: `git commit -m "feat: add my feature"`
5. Push: `git push origin feature/my-feature`
6. Create pull request

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

## Resources

- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Mem0 Docs](https://docs.mem0.ai/)
