# 🎮 Interactive Testing Guide for AgentAru

## ✅ All Setup Complete!

Your AgentAru is now fully configured with:
- 🏠 **Local LLM**: Qwen2.5 7B Instruct
- 🧠 **Local Memory**: Nomic embeddings + Qdrant vector DB
- 🔧 **MCP Tools**: 4 filesystem tools
- 🚫 **Zero Cloud Dependencies**: No API keys needed!

---

## 🚀 Quick Start - Web UI (Recommended)

### Launch the Interface:
```bash
cd /Users/aravindgillella/projects/agentAru
source .venv/bin/activate
streamlit run app.py
```

### Then:
1. Open browser to: **http://localhost:8501**
2. Click **"🚀 Initialize Agent"** in sidebar
3. Wait for initialization (~5 seconds)
4. Start chatting!

### What You'll See:
- **Left Sidebar**: Model info, MCP tools, memory stats, actions
- **Main Area**: Chat interface
- **Status**: Green checkmark when ready

---

## 💬 What to Try

### 1. Basic Questions
```
What is machine learning?
Explain quantum computing
Write a haiku about AI
```

### 2. Math & Logic
```
What is 2+2?
Calculate the factorial of 5
Solve: 3x + 7 = 22
```

### 3. Coding Help
```
Write a Python function to reverse a string
Explain list comprehension in Python
What's the difference between == and is in Python?
```

### 4. File Operations (MCP Tools)
```
List files in the current directory
Read the contents of README.md
Create a new directory called test_folder
```

### 5. Memory Test
After chatting, ask:
```
What did we talk about earlier?
Remind me what I asked you
```

---

## 🖥️ Alternative: Command Line Interface

### Launch CLI:
```bash
python3 run_agent.py
```

### Special Commands:
- `mcp list` - Show all MCP tools
- `memory` - Search conversation history
- `exit` - Quit

### Example Session:
```
You: What is Python?
AgentAru: [explains Python...]

You: mcp list
📦 Available MCP Tools:
  - filesystem_read_file: Read contents of a file
  - filesystem_write_file: Write content to a file
  - filesystem_list_directory: List contents of a directory
  - filesystem_create_directory: Create a new directory

You: memory
🧠 Found 1 memories:
  1. User asked about Python programming language...

You: exit
👋 Goodbye!
```

---

## 🎯 Testing Checklist

### Basic Functionality
- [ ] Agent initializes without errors
- [ ] Chat responses are coherent
- [ ] Response time is reasonable (few seconds)

### Memory System
- [ ] No OpenAI API errors
- [ ] Conversations are remembered
- [ ] Memory search works

### MCP Tools
- [ ] All 4 tools listed
- [ ] Filesystem operations work
- [ ] No connection errors

### UI/UX
- [ ] Web UI loads properly
- [ ] Sidebar shows correct info
- [ ] Chat messages display nicely
- [ ] Clear chat button works

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "Ollama not running"
```bash
brew services restart ollama
ollama list  # Verify models
```

### "Memory dimension error"
```bash
rm -rf ./data/vector_db
mkdir -p ./data/vector_db
# Then restart agent
```

### "Port 8501 already in use"
```bash
# Kill existing Streamlit
pkill -f streamlit
# Or use different port
streamlit run app.py --server.port=8502
```

---

## 📊 Performance Expectations

### Response Times:
- **Simple questions**: 1-3 seconds
- **Complex explanations**: 3-8 seconds
- **Code generation**: 5-10 seconds

### Memory:
- **RAM usage**: ~2-4 GB (Qwen2.5 model)
- **Disk**: ~5 GB (models + vector DB)

### Quality:
- **Accuracy**: Good for general knowledge
- **Code**: Decent Python/JS/etc
- **Memory**: Remembers recent conversations
- **Tools**: Reliable file operations

---

## 🎨 Customization Ideas

### Change Model:
Edit `.env`:
```env
DEFAULT_MODEL=ollama/llama3.2:3b-instruct  # Faster, smaller
# or
DEFAULT_MODEL=ollama/qwen2.5:7b-instruct   # Current (balanced)
```

### Add More MCP Tools:
Edit `src/mcp_integration/mcp_servers.yaml` to enable:
- Web search (Brave)
- GitHub operations
- SQLite database
- Slack integration

### Adjust Temperature:
In `run_agent.py` or `app.py`, modify:
```python
llm = model_manager.get_model(temperature=0.7)  # Creative
llm = model_manager.get_model(temperature=0.2)  # Focused
```

---

## 🏆 Success Indicators

You'll know it's working when:
- ✅ No API key errors in logs
- ✅ Chat responses are contextual
- ✅ Memory searches return results
- ✅ MCP tools are listed in sidebar
- ✅ File operations succeed
- ✅ UI is responsive

---

## 📝 Notes

**Local vs Cloud:**
- This setup is 100% local
- No data sent to OpenAI/Anthropic
- All processing on your machine
- Privacy-first architecture

**Limitations:**
- Tool calling quality depends on model
- Memory is local only (no cloud sync)
- Performance depends on your hardware
- Not as capable as GPT-4/Claude for complex tasks

**Best Use Cases:**
- Privacy-sensitive work
- Offline development
- Learning AI/LLM concepts
- Prototyping agent architectures
- Cost-free experimentation

---

## 🎉 Ready to Test!

**Choose your adventure:**

### For Visual Experience:
```bash
streamlit run app.py
```

### For Terminal Simplicity:
```bash
python3 run_agent.py
```

**Happy chatting with your local AI agent!** 🤖
