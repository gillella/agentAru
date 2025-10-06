# 🚀 Running AgentAru

## Prerequisites

Make sure you have:
- ✅ Ollama installed and running
- ✅ Qwen2.5:7b-instruct model pulled
- ✅ nomic-embed-text model pulled
- ✅ Virtual environment activated

## Quick Start

### Option 1: Web UI (Recommended) 🌐

```bash
streamlit run app.py
```

Then open: **http://localhost:8501**

**Features:**
- Beautiful chat interface
- Real-time responses
- Memory tracking
- MCP tools display
- 100% local (no API keys)

---

### Option 2: Command Line 💻

```bash
python3 run_agent.py
```

**Interactive commands:**
- Type your questions normally
- `mcp list` - Show available tools
- `memory` - Search conversation history
- `exit` - Quit

---

## What You Can Ask

### General Questions
```
What is machine learning?
Explain quantum computing in simple terms
Write a Python function to calculate fibonacci numbers
```

### File Operations (via MCP)
```
List files in the current directory
Read the contents of README.md
Create a new directory called "test"
```

### Memory Queries
```
What did we discuss earlier?
Remind me what I asked about yesterday
```

---

## System Information

**Model:** Qwen2.5 7B Instruct (local via Ollama)
**Memory:** Local vector store (Qdrant + Nomic embeddings)
**Tools:** MCP filesystem server (4 tools)

**No cloud dependencies!** Everything runs locally on your machine.

---

## Troubleshooting

**Agent won't start?**
```bash
# Check Ollama is running
ollama list

# Restart Ollama if needed
brew services restart ollama
```

**Memory errors?**
```bash
# Clear vector database
rm -rf ./data/vector_db
mkdir -p ./data/vector_db
```

**Import errors?**
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

1. **Try the Web UI** - Most user-friendly
2. **Test MCP tools** - File operations
3. **Check memory** - See what it remembers
4. **Add more tools** - Extend with custom MCP servers

Enjoy your local AI agent! 🎉
