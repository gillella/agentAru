# AgentAru API Reference

## Core Components

### ModelManager

**Location**: `src/core/model_manager.py`

Manages multiple LLM providers with dynamic switching and caching.

#### Methods

##### `__init__(config_path: str = "src/config/models.yaml")`
Initialize the model manager.

**Parameters**:
- `config_path`: Path to models YAML configuration

**Example**:
```python
from src.core.model_manager import ModelManager

manager = ModelManager()
```

##### `get_model(model_name: str = None, temperature: float = 0.7, **kwargs)`
Get a LangChain model instance.

**Parameters**:
- `model_name`: Model identifier (e.g., "anthropic/claude-3-5-sonnet-20241022")
- `temperature`: Model temperature (0.0-1.0)
- `**kwargs`: Additional model parameters

**Returns**: LangChain chat model instance

**Example**:
```python
llm = manager.get_model("anthropic/claude-3-5-sonnet-20241022", temperature=0.7)
```

##### `list_models(provider: str = None) -> List[ModelConfig]`
List available models.

**Parameters**:
- `provider`: Optional provider filter ("anthropic", "openai", "ollama")

**Returns**: List of ModelConfig objects

##### `switch_model(new_model: str, temperature: float = 0.7, **kwargs)`
Switch to a different model.

**Parameters**:
- `new_model`: New model identifier
- `temperature`: Model temperature
- `**kwargs`: Additional parameters

**Returns**: New model instance

---

### AgentMemoryManager

**Location**: `src/memory/memory_manager.py`

Long-term memory system with temporal decay.

#### Methods

##### `__init__(user_id: str = "default_user", api_key: str = None, config: Dict[str, Any] = None)`
Initialize memory manager.

**Parameters**:
- `user_id`: Unique user identifier
- `api_key`: Mem0 API key (optional for local mode)
- `config`: Memory configuration dict

**Example**:
```python
from src.memory.memory_manager import AgentMemoryManager

memory = AgentMemoryManager(
    user_id="user123",
    config={"decay_days": 90}
)
```

##### `add_interaction(messages: List[BaseMessage], metadata: Dict[str, Any] = None) -> str`
Store conversation interaction.

**Parameters**:
- `messages`: List of LangChain messages
- `metadata`: Optional metadata dict

**Returns**: Memory ID

**Example**:
```python
from langchain_core.messages import HumanMessage, AIMessage

messages = [
    HumanMessage(content="Hello"),
    AIMessage(content="Hi there!")
]

memory_id = memory.add_interaction(messages, metadata={"session": "abc123"})
```

##### `add_fact(fact: str, category: str = "general", metadata: Dict[str, Any] = None) -> str`
Store semantic knowledge.

**Parameters**:
- `fact`: Fact or knowledge to store
- `category`: Category classification
- `metadata`: Optional metadata

**Returns**: Memory ID

**Example**:
```python
memory.add_fact(
    fact="User prefers morning meetings",
    category="preferences",
    metadata={"confidence": 0.9}
)
```

##### `add_procedure(task: str, steps: List[str], metadata: Dict[str, Any] = None) -> str`
Store procedural knowledge.

**Parameters**:
- `task`: Task description
- `steps`: List of steps
- `metadata`: Optional metadata

**Returns**: Memory ID

**Example**:
```python
memory.add_procedure(
    task="Create weekly report",
    steps=[
        "Gather metrics",
        "Generate charts",
        "Write summary"
    ]
)
```

##### `search_memories(query: str, memory_type: str = None, limit: int = 5, apply_decay: bool = True) -> List[Dict[str, Any]]`
Search relevant memories.

**Parameters**:
- `query`: Search query
- `memory_type`: Filter by type ("episodic", "semantic", "procedural")
- `limit`: Maximum results
- `apply_decay`: Apply temporal decay

**Returns**: List of memory dicts with scores

**Example**:
```python
results = memory.search_memories(
    query="meeting preferences",
    memory_type="semantic",
    limit=5
)

for result in results:
    print(f"{result['memory']} (score: {result['score']})")
```

##### `get_context_for_query(query: str, max_tokens: int = 2000) -> str`
Get formatted context string.

**Parameters**:
- `query`: Query for context
- `max_tokens`: Maximum token budget

**Returns**: Formatted context string

---

### AgentAruGraph

**Location**: `src/core/agent_graph.py`

LangGraph orchestrator for multi-agent workflows.

#### Methods

##### `__init__(model_manager: ModelManager, memory_manager: AgentMemoryManager, user_id: str = "default_user")`
Initialize agent graph.

**Parameters**:
- `model_manager`: ModelManager instance
- `memory_manager`: AgentMemoryManager instance
- `user_id`: User identifier

##### `compile(checkpointer=None)`
Compile the graph for execution.

**Parameters**:
- `checkpointer`: Optional checkpointer (default: MemorySaver)

**Returns**: Compiled graph app

##### `run(user_input: str, session_id: str = None) -> Dict[str, Any]`
Run agent synchronously.

**Parameters**:
- `user_input`: User query
- `session_id`: Optional session ID

**Returns**: Final state dict

**Example**:
```python
from src.core.agent_graph import AgentAruGraph

graph = AgentAruGraph(model_manager, memory_manager)
graph.compile()

result = graph.run("Read my emails")

# Access response
response = result["messages"][-1].content
print(response)
```

##### `async arun(user_input: str, session_id: str = None) -> Dict[str, Any]`
Run agent asynchronously.

**Parameters**:
- `user_input`: User query
- `session_id`: Optional session ID

**Returns**: Final state dict

---

## Agent Classes

### SupervisorAgent

**Location**: `src/agents/supervisor_agent.py`

Routes requests to specialized agents.

#### Methods

##### `__init__(model_manager: ModelManager, memory_manager: AgentMemoryManager)`
Initialize supervisor.

##### `process(state: AgentState) -> AgentState`
Process state and route to agent.

**Parameters**:
- `state`: Current agent state

**Returns**: Updated state with routing decision

---

### EmailAgent

**Location**: `src/agents/email_agent.py`

Handles email operations.

#### Methods

##### `__init__(model_manager: ModelManager, memory_manager: AgentMemoryManager)`
Initialize email agent.

##### `process(state: AgentState) -> AgentState`
Process email task.

**Parameters**:
- `state`: Current agent state

**Returns**: Updated state with email results

---

### CalendarAgent

**Location**: `src/agents/calendar_agent.py`

Manages calendar and scheduling.

#### Methods

##### `__init__(model_manager: ModelManager, memory_manager: AgentMemoryManager)`
Initialize calendar agent.

##### `process(state: AgentState) -> AgentState`
Process calendar task.

**Parameters**:
- `state`: Current agent state

**Returns**: Updated state with calendar results

---

### IdeaAgent

**Location**: `src/agents/idea_agent.py`

Captures and organizes ideas.

#### Methods

##### `__init__(model_manager: ModelManager, memory_manager: AgentMemoryManager)`
Initialize idea agent.

##### `process(state: AgentState) -> AgentState`
Process idea task.

**Parameters**:
- `state`: Current agent state

**Returns**: Updated state with idea results

---

## Integration Classes

### GmailIntegration

**Location**: `src/integrations/gmail.py`

Gmail API wrapper.

#### Methods

##### `__init__(credentials_path: str = "credentials.json")`
Initialize Gmail integration.

**Parameters**:
- `credentials_path`: Path to OAuth credentials

##### `read_emails(max_results: int = 10, query: str = None, label: str = "INBOX") -> List[Dict[str, Any]]`
Read emails from Gmail.

**Parameters**:
- `max_results`: Maximum emails to fetch
- `query`: Gmail search query
- `label`: Label filter

**Returns**: List of email dicts

**Example**:
```python
from src.integrations.gmail import GmailIntegration

gmail = GmailIntegration()

# Read unread emails
emails = gmail.read_emails(query="is:unread", max_results=5)

for email in emails:
    print(f"{email['subject']} from {email['from']}")
```

##### `send_email(to: str, subject: str, body: str, cc: List[str] = None, bcc: List[str] = None) -> Dict[str, str]`
Send an email.

**Parameters**:
- `to`: Recipient email
- `subject`: Email subject
- `body`: Email body
- `cc`: CC recipients (optional)
- `bcc`: BCC recipients (optional)

**Returns**: Result dict with status

**Example**:
```python
result = gmail.send_email(
    to="user@example.com",
    subject="Test Email",
    body="This is a test message"
)

if result["status"] == "sent":
    print(f"Email sent: {result['message_id']}")
```

---

## State Types

### AgentState

**Location**: `src/core/state.py`

Typed dictionary for agent state.

#### Fields

```python
{
    "messages": List[BaseMessage],           # Conversation messages
    "current_task": str,                     # Current task description
    "user_query": str,                       # Original user query
    "relevant_memories": List[Dict],         # Retrieved memories
    "episodic_context": str,                 # Episodic memory context
    "semantic_context": str,                 # Semantic memory context
    "next_agent": str,                       # Next agent to call
    "agent_history": List[str],              # Agent execution history
    "email_results": Optional[Dict],         # Email agent results
    "calendar_results": Optional[Dict],      # Calendar agent results
    "idea_results": Optional[Dict],          # Idea agent results
    "timestamp": datetime,                   # Request timestamp
    "user_id": str,                          # User identifier
    "session_id": str,                       # Session identifier
    "errors": List[str],                     # Error messages
    "retry_count": int                       # Retry counter
}
```

---

## Configuration

### Settings

**Location**: `src/config/settings.py`

Application settings (Pydantic BaseSettings).

#### Fields

```python
class Settings:
    # Model Configuration
    default_model: str = "anthropic/claude-3-5-sonnet-20241022"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    # Memory Configuration
    memory_provider: str = "mem0"
    chroma_persist_directory: Path = Path("./data/vector_db")
    memory_decay_days: int = 90

    # Google APIs
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8501"

    # Application Settings
    debug: bool = True
    log_level: str = "INFO"
    data_dir: Path = Path("./data")
```

**Usage**:
```python
from src.config.settings import settings

print(settings.default_model)
print(settings.memory_decay_days)
```

---

## Utilities

### Logger

**Location**: `src/utils/logger.py`

#### Functions

##### `setup_logger(name: str = "agentaru", level: str = "INFO", log_file: str = None, log_dir: str = "logs") -> logging.Logger`
Setup application logger.

**Parameters**:
- `name`: Logger name
- `level`: Log level
- `log_file`: Optional log file
- `log_dir`: Log directory

**Returns**: Configured logger

**Example**:
```python
from src.utils.logger import setup_logger

logger = setup_logger(name="my_module", level="DEBUG")
logger.info("Application started")
```

---

## Data Models

### ModelConfig

**Location**: `src/core/model_manager.py`

Model configuration Pydantic model.

```python
class ModelConfig(BaseModel):
    name: str
    display_name: str
    context_window: int
    cost_per_1k_tokens: Optional[Dict[str, float]] = None
    local: bool = False
    capabilities: List[str] = []
```

### MemoryEntry

**Location**: `src/memory/schemas.py`

Memory entry Pydantic model.

```python
class MemoryEntry(BaseModel):
    id: str
    content: str
    memory_type: str  # episodic, semantic, procedural
    metadata: Dict[str, Any]
    timestamp: datetime
    relevance_score: float = 1.0
    decay_factor: float = 1.0
```

---

## Usage Examples

### Complete Application Flow

```python
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import components
from src.core.model_manager import ModelManager
from src.core.agent_graph import AgentAruGraph
from src.memory.memory_manager import AgentMemoryManager
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.email_agent import EmailAgent
from src.agents.calendar_agent import CalendarAgent
from src.agents.idea_agent import IdeaAgent

# Initialize
model_manager = ModelManager()
memory_manager = AgentMemoryManager(
    user_id="user123",
    config={"decay_days": 90}
)

# Create agents
supervisor = SupervisorAgent(model_manager, memory_manager)
email_agent = EmailAgent(model_manager, memory_manager)
calendar_agent = CalendarAgent(model_manager, memory_manager)
idea_agent = IdeaAgent(model_manager, memory_manager)

# Build graph
graph = AgentAruGraph(model_manager, memory_manager, user_id="user123")
graph.set_agents(
    supervisor=supervisor,
    email=email_agent,
    calendar=calendar_agent,
    idea=idea_agent
)

# Compile
graph.compile()

# Run
result = graph.run("Read my recent emails")

# Get response
response = result["messages"][-1].content
print(response)

# Check which agents were used
print(f"Agents used: {result['agent_history']}")
```

### Custom Agent Example

```python
from typing import Dict, Any
from langchain_core.messages import AIMessage, SystemMessage
from src.core.state import AgentState

class CustomAgent:
    def __init__(self, model_manager, memory_manager):
        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.llm = model_manager.get_model()

    def process(self, state: AgentState) -> AgentState:
        # Get context from memory
        memories = self.memory_manager.search_memories(
            query=state["user_query"],
            limit=3
        )

        # Build prompt
        context = self._build_context(state["user_query"], memories)

        # Get LLM response
        response = self.llm.invoke([
            SystemMessage(content=context),
            *state["messages"]
        ])

        # Update state
        state["custom_results"] = {"message": response.content}
        state["agent_history"].append("custom_agent")
        state["messages"].append(AIMessage(content=response.content))
        state["next_agent"] = ""

        return state

    def _build_context(self, query, memories):
        return f"Context: {query}"
```

---

## Error Handling

All methods follow consistent error handling:

```python
try:
    # Operation
    result = do_something()
    logger.info("Success")
    return result

except SpecificError as e:
    logger.error(f"Specific error: {e}")
    return default_value

except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

---

## Type Hints

All public methods include type hints:

```python
def method_name(
    param1: str,
    param2: int = 10,
    param3: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Method documentation"""
    pass
```

---

## Testing

### Test Fixtures

Available in `tests/conftest.py`:

- `mock_model_manager`: Mocked ModelManager
- `mock_memory_manager`: Mocked AgentMemoryManager
- `sample_state`: Sample AgentState for testing

**Example**:
```python
def test_my_function(mock_model_manager, mock_memory_manager):
    agent = MyAgent(mock_model_manager, mock_memory_manager)
    assert agent is not None
```
