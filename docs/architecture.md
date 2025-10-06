# AgentAru Architecture

## Overview

AgentAru is built on a multi-agent architecture using LangGraph for orchestration, with three key components:

1. **Multi-Model Support** - Flexible LLM provider abstraction
2. **Long-Term Memory** - Persistent memory with temporal decay
3. **Specialized Agents** - Task-specific agents coordinated by a supervisor

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                   User Interface                 │
│              (CLI / Streamlit UI)               │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              AgentAru Graph                      │
│           (LangGraph Orchestrator)               │
│                                                  │
│  ┌─────────────┐         ┌──────────────────┐   │
│  │ Supervisor  │────────▶│  Memory Update   │   │
│  │   Agent     │         │      Node        │   │
│  └──────┬──────┘         └──────────────────┘   │
│         │                                        │
│         ├─────────┬─────────┬─────────┐         │
│         ▼         ▼         ▼         ▼         │
│    ┌────────┐ ┌────────┐ ┌────────┐ ┌────┐     │
│    │ Email  │ │Calendar│ │  Idea  │ │... │     │
│    │ Agent  │ │ Agent  │ │ Agent  │ └────┘     │
│    └────────┘ └────────┘ └────────┘             │
└─────────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ Model        │          │   Memory     │
│ Manager      │          │   Manager    │
│              │          │              │
│ • Claude     │          │ • Mem0       │
│ • GPT-4      │          │ • ChromaDB   │
│ • Ollama     │          │ • Decay      │
└──────────────┘          └──────────────┘
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ Integrations │          │ Vector Store │
│              │          │              │
│ • Gmail      │          │ • Embeddings │
│ • Calendar   │          │ • Similarity │
└──────────────┘          └──────────────┘
```

## Core Components

### 1. Agent Graph (LangGraph)

**File**: `src/core/agent_graph.py`

The central orchestrator managing workflow between agents:

```python
StateGraph Flow:
1. User Input → Supervisor Node
2. Supervisor → Route to Specialized Agent
3. Specialized Agent → Process Task
4. Return to Supervisor → Check if done
5. If done → Memory Update → End
6. If not done → Route to next agent
```

**Key Features**:
- Stateful conversation flow
- Conditional routing based on supervisor decisions
- Checkpointing for conversation persistence
- Error recovery and retry logic

### 2. Model Manager

**File**: `src/core/model_manager.py`

Abstraction layer for multiple LLM providers:

```python
ModelManager
├── Load configs from YAML
├── Detect provider (Anthropic/OpenAI/Ollama)
├── Validate API keys
├── Create model instances
├── Cache models for reuse
└── Switch models dynamically
```

**Supported Models**:
- **Anthropic**: Claude 3.5 Sonnet, Claude 3.5 Haiku
- **OpenAI**: GPT-4o, GPT-4o-mini
- **Ollama**: Llama 3.1, Mistral, etc.

### 3. Memory System

**Files**:
- `src/memory/memory_manager.py`
- `src/memory/vector_store.py`

Dual-layer memory architecture:

#### Layer 1: Mem0 (Semantic Memory)
```python
Memory Types:
├── Episodic: Conversation history
├── Semantic: Facts and knowledge
└── Procedural: How-to instructions
```

#### Layer 2: ChromaDB (Vector Store)
```python
Vector Storage:
├── Embeddings: sentence-transformers
├── Similarity Search
└── Local persistence
```

**Memory Decay**:
```python
decay_factor = max(0.1, 1 - (days_old / decay_days))
final_score = original_score * decay_factor
```

Older memories gradually lose relevance but never fully disappear.

### 4. Agent System

#### Supervisor Agent
**File**: `src/agents/supervisor_agent.py`

Routes requests to appropriate specialized agents:

```python
Routing Logic:
1. Analyze user query
2. Retrieve relevant memories
3. Decide which agent to call
4. Handle multi-agent workflows
5. Determine when task is complete
```

#### Specialized Agents

**Email Agent** (`src/agents/email_agent.py`):
- Read/categorize emails
- Draft responses in user's style
- Send emails via Gmail API
- Manage inbox

**Calendar Agent** (`src/agents/calendar_agent.py`):
- Schedule meetings
- Check availability
- Manage events
- Set reminders

**Idea Agent** (`src/agents/idea_agent.py`):
- Capture ideas and notes
- Organize by category
- Link related concepts
- Semantic search across ideas

### 5. State Management

**File**: `src/core/state.py`

Shared state structure:

```python
AgentState {
    messages: List[BaseMessage]
    current_task: str
    user_query: str
    relevant_memories: List[Dict]
    next_agent: str
    agent_history: List[str]
    email_results: Dict
    calendar_results: Dict
    idea_results: Dict
    errors: List[str]
    # ... metadata
}
```

State flows through graph nodes, accumulating context.

## Data Flow

### Request Processing

```
1. User Input
   └─> Parse query

2. Supervisor Node
   ├─> Search relevant memories
   ├─> Analyze intent
   └─> Route to agent

3. Specialized Agent
   ├─> Get user preferences from memory
   ├─> Execute task (call tools/APIs)
   └─> Update state with results

4. Return to Supervisor
   ├─> Check if task complete
   └─> Route to next agent or end

5. Memory Update Node
   ├─> Store interaction
   ├─> Extract facts
   └─> Update knowledge base

6. Return Response
   └─> Format and deliver to user
```

### Memory Flow

```
Interaction Storage:
User Query + Agent Response
    └─> Mem0.add_interaction()
        └─> Stored as episodic memory

Fact Extraction:
Agent identifies facts
    └─> Mem0.add_fact()
        └─> Stored as semantic memory

Memory Retrieval:
User Query
    └─> Mem0.search()
        └─> Apply temporal decay
            └─> Return top-k relevant
```

## Integration Architecture

### Gmail Integration

```
Gmail API Flow:
1. OAuth2 authentication
2. List messages with query
3. Fetch full message content
4. Parse headers and body
5. Return structured data
```

**Files**:
- `src/integrations/gmail.py`
- `credentials.json` (OAuth config)
- `token.json` (Auth token)

### Vector Store Integration

```
ChromaDB Flow:
1. Initialize embeddings model
2. Create/load collection
3. Add documents with metadata
4. Similarity search with filters
5. Return ranked results
```

## UI Architecture

### Streamlit Application

**File**: `src/ui/streamlit_app.py`

Components:
1. **Chat Interface**: Main conversation UI
2. **Sidebar**: Model selection, memory controls, stats
3. **Tabs**: Email, Calendar, Ideas dedicated views
4. **Session State**: Persistent conversation history

### CLI Application

**File**: `src/main.py`

Simple command-line interface:
- REPL loop
- Session persistence
- Debug mode for agent tracing

## Extension Points

### Adding New Agents

1. Create agent class in `src/agents/`
2. Implement `process(state) -> state` method
3. Add node to graph in `agent_graph.py`
4. Update supervisor routing logic

### Adding New Tools

1. Create tool in `src/tools/`
2. Use `@tool` decorator
3. Bind to agent LLM
4. Document in agent context

### Adding New Integrations

1. Create integration in `src/integrations/`
2. Implement authentication
3. Create wrapper methods
4. Add to relevant agent

### Adding New Models

1. Update `src/config/models.yaml`
2. Add provider logic in `model_manager.py`
3. Install provider package
4. Test model switching

## Configuration

### models.yaml Structure

```yaml
models:
  provider_name:
    - name: model-id
      display_name: "Display Name"
      context_window: 128000
      cost_per_1k_tokens:
        input: 0.001
        output: 0.002
      local: false
      capabilities: [chat, tool_use]
```

### Environment Variables

```bash
# Model config
DEFAULT_MODEL=provider/model-id

# API keys
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...

# Memory config
MEMORY_DECAY_DAYS=90
CHROMA_PERSIST_DIRECTORY=./data/vector_db

# App config
DEBUG=true
LOG_LEVEL=INFO
```

## Performance Considerations

### Model Selection
- **Fast tasks**: Use Haiku or GPT-4o-mini
- **Complex reasoning**: Use Sonnet or GPT-4o
- **Local/private**: Use Ollama models

### Memory Optimization
- Limit memory search results (default: 5)
- Apply temporal decay to reduce old noise
- Use token budgets for context

### Caching
- Model instances cached
- Vector embeddings cached
- API responses can be cached

## Security

### API Keys
- Stored in `.env` (gitignored)
- Never hardcoded
- Validated before use

### OAuth Tokens
- Stored locally in `token.json`
- Auto-refresh when expired
- Scoped to minimum required

### Data Privacy
- All data stored locally
- No telemetry by default
- Memory export/import for backups

## Testing Architecture

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── test_agents/         # Agent tests
├── test_core/           # Core component tests
├── test_memory/         # Memory system tests
└── test_integrations/   # Integration tests
```

### Testing Strategy
- Unit tests with mocks for external services
- Integration tests for full workflows
- Fixture-based test data
- Coverage targeting >80%

## Deployment

### Local Development
```bash
python src/main.py
# or
streamlit run src/ui/streamlit_app.py
```

### Production Considerations
- Use production API keys
- Set DEBUG=false
- Configure proper logging
- Monitor token usage
- Implement rate limiting
- Add authentication to UI

## Future Enhancements

1. **Multi-Agent Parallelization**: Run independent agents concurrently
2. **Advanced Memory**: Implement memory consolidation and pruning
3. **Tool Calling**: Full LangChain tool integration
4. **Streaming**: Real-time token streaming in UI
5. **Analytics**: Usage tracking and insights
6. **Mobile**: React Native or Flutter app
7. **Voice**: Speech-to-text integration
8. **Plugins**: Community-contributed agents
