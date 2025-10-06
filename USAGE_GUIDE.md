# AgentAru Usage Guide

## Web Search Functionality

The web search is **fully functional**, but you need to understand how it works:

### How Tool Calling Works

The LLM (Qwen 2.5) decides when to use tools based on your query. It won't always call tools for every question.

### Prompts That Work Well

✅ **Good prompts that trigger web search:**
- "Search the web for latest news about AI"
- "Find recent articles about Python programming"
- "Look up current weather in New York"
- "Search for today's top technology news"

❌ **Prompts that may NOT trigger search:**
- "What is today's date?" (LLM thinks it knows)
- "Tell me about Python" (LLM has training data)
- "What time is it?" (LLM might try to answer from memory)

### Testing Web Search

**Using CLI:**
```bash
python run_agent.py
```

Then ask:
```
Search the web for latest AI developments
```

**Using Streamlit UI:**
```bash
streamlit run app.py
```

1. Click "Initialize Agent"
2. Wait for both servers to connect (filesystem + web-search)
3. In the chat, type: "Search the web for current events"

### Expected Behavior

When web search is triggered, you'll see:
1. Agent receives your query
2. Agent calls `web-search_search_web` tool
3. Tool returns DuckDuckGo search results
4. Agent formats and presents the results

### Example Working Query

```
User: Search the web for latest news about AI

Agent: [Calls search_web tool]
Here are some of the latest news articles about AI:

1. **Google News - Artificial intelligence**
   You can read full articles, watch videos, and browse thousands of titles...

2. **TechCrunch - AI News**
   TechCrunch covers the latest in artificial intelligence...

[etc.]
```

### Troubleshooting

**If search doesn't work:**

1. **Check servers are connected:**
   ```
   # In CLI, type:
   mcp list

   # You should see:
   - web-search_search_web
   - web-search_get_page_content
   ```

2. **Use explicit search phrases:**
   - Start with "Search the web for..."
   - Say "Look up online..."
   - Ask "Find recent articles about..."

3. **Check Streamlit sidebar:**
   - Should show "✅ MCP web-search server connected"
   - Should list 6 tools (4 filesystem + 2 web search)

### Direct Testing

To verify web search works independently:
```bash
python test_agent_search.py
```

This will directly test the search functionality without relying on LLM decision-making.

## Available Tools

### Web Search Tools (2)
- `search_web` - Search DuckDuckGo and get results
- `get_page_content` - Fetch content from a specific URL

### Filesystem Tools (4)
- `read_file` - Read file contents
- `write_file` - Write to a file
- `list_directory` - List directory contents
- `create_directory` - Create a new directory

## Memory System

The agent stores conversation history using:
- **Embeddings:** Local Nomic-embed-text model
- **Vector DB:** Qdrant (local file-based)
- **LLM:** Qwen 2.5 7B for memory extraction

No cloud services or API keys needed!
