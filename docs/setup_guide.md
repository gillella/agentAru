# AgentAru Setup Guide

## Prerequisites

- Python 3.11 or higher
- pip package manager
- (Optional) Gmail account for email features
- (Optional) Google Calendar for calendar features
- API key for at least one LLM provider (Anthropic, OpenAI, or Ollama)

## Installation

### 1. Automated Setup (Recommended)

```bash
# Run the setup script
bash scripts/setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Setup the .env file from template

### 2. Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/vector_db data/memory data/cache logs

# Setup environment
cp .env.example .env
```

## Configuration

### 1. API Keys

Edit `.env` and add your API keys:

```bash
# For Claude
ANTHROPIC_API_KEY=your-anthropic-key

# For GPT-4
OPENAI_API_KEY=your-openai-key

# For local models (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Gmail Integration (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials as `credentials.json`
6. Place `credentials.json` in project root

### 3. Google Calendar Integration (Optional)

1. In same Google Cloud project
2. Enable Google Calendar API
3. Use same OAuth credentials

### 4. Memory Configuration

Adjust memory settings in `.env`:

```bash
MEMORY_DECAY_DAYS=90  # How long before memories decay
CHROMA_PERSIST_DIRECTORY=./data/vector_db
```

## Running AgentAru

### CLI Mode

```bash
python src/main.py
```

### Web UI (Streamlit)

```bash
streamlit run src/ui/streamlit_app.py
```

The UI will open at `http://localhost:8501`

## First Time Setup

### 1. Gmail Authorization

On first email operation:
- Browser will open for Google OAuth
- Grant permissions
- Token saved as `token.json` for future use

### 2. Download Embedding Model

The first run will download the sentence transformer model (~80MB):

```python
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### 3. Test the System

Try these test queries:

```
# General chat
"Hello, what can you do?"

# Email (requires Gmail setup)
"Read my recent emails"

# Calendar (requires Calendar setup)
"What's on my calendar today?"

# Ideas
"Save this idea: Build a task automation system"
```

## Model Configuration

### Using Different Models

Edit `src/config/models.yaml` to add/modify models:

```yaml
models:
  anthropic:
    - name: claude-3-5-sonnet-20241022
      display_name: "Claude 3.5 Sonnet"
      context_window: 200000
      capabilities: [chat, tool_use, vision]
```

### Switching Models

In `.env`:

```bash
DEFAULT_MODEL=anthropic/claude-3-5-sonnet-20241022
```

Or in UI: Use the model selector in sidebar

### Using Local Models (Ollama)

1. Install Ollama: https://ollama.ai
2. Pull a model:

```bash
ollama pull llama3.1:8b
```

3. Select in UI or set in `.env`:

```bash
DEFAULT_MODEL=ollama/llama3.1:8b
```

## Troubleshooting

### Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Memory Issues

```bash
# Clear vector database
rm -rf data/vector_db/*

# Restart application
```

### Gmail Authorization Issues

```bash
# Remove old token
rm token.json

# Re-authorize on next run
```

### Model Loading Errors

Check:
1. API key is correct in `.env`
2. API key has credits/quota
3. Model name is correct

## Advanced Configuration

### Custom Agents

Add new agents in `src/agents/`:

```python
from src.core.state import AgentState

class CustomAgent:
    def __init__(self, model_manager, memory_manager):
        # Implementation
        pass

    def process(self, state: AgentState) -> AgentState:
        # Logic
        return state
```

### Custom Tools

Add tools in `src/tools/`:

```python
from langchain.tools import tool

@tool
def custom_tool(param: str) -> str:
    """Tool description"""
    # Implementation
    return result
```

## Production Deployment

### Environment Variables

Set production values:

```bash
DEBUG=false
LOG_LEVEL=INFO
```

### Security

- Keep `.env` and credentials files secure
- Never commit API keys to version control
- Use environment variables in production

### Performance

- Use faster models for quick tasks (Haiku, GPT-4o-mini)
- Implement caching for repeated queries
- Monitor token usage and costs

## Next Steps

- Read [Architecture Overview](architecture.md)
- Explore [API Reference](api_reference.md)
- Check [Development Guide](development_guide.md)
