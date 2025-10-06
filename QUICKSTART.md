# 🚀 AgentAru Quick Start

Get up and running with AgentAru + MCP in 5 minutes!

## Step 1: Install (2 min)

```bash
# Clone the repository (if not already done)
cd agentaru

# Run automated setup
bash scripts/setup.sh

# Or manual setup
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Configure (1 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# For Claude (recommended):
ANTHROPIC_API_KEY=your-key-here

# Or for GPT-4:
# OPENAI_API_KEY=your-key-here
```

## Step 3: Run (1 min)

### Option A: MCP-Enabled CLI (Recommended) 🔥

```bash
python src/main_mcp.py
```

**Try MCP features:**
```
You: mcp servers           # List connected servers
You: mcp connect filesystem
You: Read the README.md file
You: List files in src/
```

### Option B: Web UI

```bash
streamlit run src/ui/streamlit_app.py
```

Opens at http://localhost:8501

### Option C: Standard CLI

```bash
python src/main.py
```

## Step 4: Test (1 min)

Try these example queries:

### General Chat
```
"Hello! What can you help me with?"
```

### Ideas & Notes
```
"Save this idea: Build an AI-powered task automation system"
"Show me my ideas about automation"
```

### Email (requires Gmail setup)
```
"Read my recent emails"
"Draft an email to john@example.com about the project update"
```

### Calendar (requires Google Calendar setup)
```
"What's on my calendar today?"
"Schedule a meeting for tomorrow at 2pm"
```

## Quick Tips

### Switch Models
In Streamlit UI: Use sidebar dropdown

In CLI: Edit `.env`:
```bash
DEFAULT_MODEL=anthropic/claude-3-5-haiku-20241022  # Faster, cheaper
```

### Gmail Setup (Optional)

1. Get credentials: https://console.cloud.google.com/
2. Enable Gmail API
3. Download `credentials.json` to project root
4. First email operation will open browser for OAuth

### Memory Management

View all memories:
```python
# In Streamlit: Click "View Memories" in sidebar
```

Export conversation:
```python
# In Streamlit: Click "Export" → "Download Conversation"
```

## Common Issues

### Import errors
```bash
source .venv/bin/activate  # Ensure venv is active
```

### API key errors
```bash
# Check .env file has correct key
cat .env | grep API_KEY
```

### Model loading errors
```bash
# Check model name is correct
grep DEFAULT_MODEL .env
```

## Next Steps

📖 **Learn More**:
- [Full Setup Guide](docs/setup_guide.md)
- [Architecture Overview](docs/architecture.md)
- [Development Guide](docs/development_guide.md)

🛠️ **Customize**:
- Add new agents in `src/agents/`
- Add new tools in `src/tools/`
- Modify models in `src/config/models.yaml`

🤝 **Contribute**:
- Report issues on GitHub
- Submit pull requests
- Share your custom agents

---

**Need Help?** Check the [Setup Guide](docs/setup_guide.md) or create an issue.
