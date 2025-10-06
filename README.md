# 🤖 AgentAru - AI-Native Personal Assistant

A powerful personal AI assistant built with LangGraph and LangChain, featuring multi-LLM support, long-term memory, and intelligent task automation.

## ✨ Features

- **Multi-Model Support**: Seamlessly switch between Claude, GPT-4, and local models (Ollama)
- **MCP Integration** 🔥: Full Model Context Protocol support for standardized tool access
- **Long-Term Memory**: Persistent memory with temporal decay using Mem0 and ChromaDB
- **Specialized Agents**:
  - 📧 Email Agent: Read, categorize, draft, and send emails via Gmail
  - 📅 Calendar Agent: Manage schedules and meetings with Google Calendar
  - 💡 Idea Agent: Capture and organize notes and ideas
  - 🔧 MCP Agent: Access to filesystem, web search, GitHub, Slack, and more via MCP servers
- **Intelligent Routing**: Supervisor agent orchestrates multi-agent workflows
- **Beautiful UI**: Streamlit-based web interface

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Gmail API credentials (for email features)
- Google Calendar API credentials (for calendar features)
- API keys for LLM providers (Anthropic, OpenAI, or Ollama)

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd agentaru
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

5. Run the application:
```bash
streamlit run src/ui/streamlit_app.py
```

## 📁 Project Structure

```
agentaru/
├── src/
│   ├── config/          # Configuration management
│   ├── core/            # Core agent graph and model manager
│   ├── memory/          # Long-term memory system
│   ├── agents/          # Specialized agents
│   ├── integrations/    # External API integrations
│   ├── tools/           # LangChain tools
│   └── ui/              # Streamlit interface
├── tests/               # Test suite
├── data/                # Local data storage
└── docs/                # Documentation
```

## 🔧 Configuration

### Model Configuration

Edit `src/config/models.yaml` to add or modify supported models:

```yaml
models:
  anthropic:
    - name: claude-3-5-sonnet-20241022
      context_window: 200000
```

### Memory Settings

Configure memory behavior in `.env`:

```bash
MEMORY_DECAY_DAYS=90  # Days before memories start decaying
CHROMA_PERSIST_DIRECTORY=./data/vector_db
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=src tests/
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api_reference.md)
- [Setup Guide](docs/setup_guide.md)
- [Development Guide](docs/development_guide.md)

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Mem0](https://github.com/mem0ai/mem0)
- [Streamlit](https://streamlit.io/)
