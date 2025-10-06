# MCP Integration Guide

## Overview

AgentAru now supports **MCP (Model Context Protocol)** for standardized tool access across different LLM providers. MCP provides a unified way to connect external tools, data sources, and services to your AI agents.

## What is MCP?

Model Context Protocol (MCP) is an open protocol that enables:
- **Standardized tool interfaces** across different AI models
- **Secure context sharing** from external data sources
- **Easy integration** with third-party services
- **Pluggable architecture** for adding new capabilities

## Architecture

```
AgentAru
    │
    ├── MCP Manager
    │   ├── MCP Client (connection handling)
    │   ├── Tool Manager (LangChain integration)
    │   └── Config Manager (server configuration)
    │
    ├── MCP Servers
    │   ├── Filesystem Server (built-in)
    │   ├── Web Search (Brave)
    │   ├── GitHub
    │   ├── Slack
    │   └── Custom servers...
    │
    └── Agents
        ├── MCP Agent (MCP-enhanced)
        └── Other agents (can use MCP tools)
```

## Quick Start

### 1. Basic Usage

```python
from src.mcp.manager import initialize_mcp

# Initialize MCP
mcp_manager = await initialize_mcp()

# Connect to a server
await mcp_manager.connect_server_by_name("filesystem")

# Get available tools
tools = mcp_manager.get_available_tools()

# Execute a tool
result = await mcp_manager.execute_tool(
    tool_name="filesystem_read_file",
    arguments={"path": "README.md"}
)
```

### 2. Run with MCP

```bash
# CLI with MCP
python src/main_mcp.py

# In the CLI:
You: mcp servers        # List connected servers
You: mcp tools          # List available tools
You: mcp connect github # Connect to GitHub server
```

## Configuration

### MCP Servers Configuration

Edit `src/mcp/mcp_servers.yaml`:

```yaml
servers:
  - name: filesystem
    command: python
    args:
      - src/mcp/servers/filesystem_server.py
    enabled: true
    auto_connect: false
    description: File system access tools

  - name: web-search
    command: npx
    args:
      - -y
      - '@modelcontextprotocol/server-brave-search'
    env:
      BRAVE_API_KEY: 'your-api-key'
    enabled: true
    auto_connect: false
    description: Web search via Brave API
```

### Available MCP Servers

#### Built-in Servers

**1. Filesystem Server** (Included)
- Read files
- Write files
- List directories
- Create directories

#### Official MCP Servers (npm-based)

**2. Web Search (Brave)**
```yaml
name: web-search
command: npx
args: ['-y', '@modelcontextprotocol/server-brave-search']
env:
  BRAVE_API_KEY: 'your-key'
```

**3. GitHub**
```yaml
name: github
command: npx
args: ['-y', '@modelcontextprotocol/server-github']
env:
  GITHUB_TOKEN: 'your-token'
```

**4. Google Drive**
```yaml
name: google-drive
command: npx
args: ['-y', '@modelcontextprotocol/server-gdrive']
```

**5. Slack**
```yaml
name: slack
command: npx
args: ['-y', '@modelcontextprotocol/server-slack']
env:
  SLACK_BOT_TOKEN: 'your-token'
  SLACK_TEAM_ID: 'your-team-id'
```

**6. SQLite**
```yaml
name: sqlite
command: npx
args: ['-y', '@modelcontextprotocol/server-sqlite', '--db-path', './data/db.sqlite']
```

### Environment Variables

Add to `.env`:

```bash
# MCP Server API Keys
BRAVE_API_KEY=your-brave-api-key
GITHUB_TOKEN=your-github-token
SLACK_BOT_TOKEN=your-slack-token
SLACK_TEAM_ID=your-team-id
```

## Using MCP Tools

### In Code

```python
from src.mcp.manager import get_mcp_manager
from src.agents.mcp_agent import MCPAgent

# Get MCP manager
mcp_manager = get_mcp_manager()
await mcp_manager.initialize()

# Connect to servers
await mcp_manager.connect_server_by_name("filesystem")
await mcp_manager.connect_server_by_name("web-search")

# Create MCP agent
mcp_agent = MCPAgent(
    model_manager,
    memory_manager,
    mcp_manager.mcp_client,
    mcp_manager.tool_manager
)

# Use in conversation
state = {
    "user_query": "Read the README.md file",
    # ... other state fields
}

result = await mcp_agent.aprocess(state)
```

### With LangChain

```python
# Get tools for LangChain
tools = mcp_manager.get_available_tools()

# Bind to LLM
llm_with_tools = llm.bind_tools(tools)

# Use in agent
response = llm_with_tools.invoke([
    SystemMessage(content="You have access to filesystem tools"),
    HumanMessage(content="What's in the current directory?")
])

# Process tool calls
if response.tool_calls:
    for tool_call in response.tool_calls:
        result = await mcp_manager.execute_tool(
            tool_call["name"],
            tool_call["args"]
        )
```

## Creating Custom MCP Servers

### Example: Custom Server

```python
#!/usr/bin/env python3
# my_custom_server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

app = Server("my-custom-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="my_tool",
            description="Does something useful",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "A parameter"
                    }
                },
                "required": ["param"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "my_tool":
        param = arguments.get("param")
        result = f"Processed: {param}"

        return [TextContent(
            type="text",
            text=result
        )]

async def main():
    async with stdio_server() as (read, write):
        await app.run(
            read,
            write,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Register Custom Server

Add to `mcp_servers.yaml`:

```yaml
servers:
  - name: my-custom
    command: python
    args:
      - path/to/my_custom_server.py
    enabled: true
    description: My custom MCP server
```

## MCP Manager API

### Initialization

```python
from src.mcp.manager import MCPManager, initialize_mcp

# Method 1: Direct initialization
mcp_manager = MCPManager()
await mcp_manager.initialize()

# Method 2: Using helper function
mcp_manager = await initialize_mcp(auto_connect=True)
```

### Server Management

```python
# Connect to server
await mcp_manager.connect_server_by_name("filesystem")

# Disconnect from server
await mcp_manager.disconnect_server("filesystem")

# Connect to all enabled servers
await mcp_manager.connect_all_enabled()

# Get connected servers
servers = mcp_manager.get_connected_servers()

# Get server info
info = mcp_manager.get_server_info("filesystem")
```

### Tool Management

```python
# Get all tools
tools = mcp_manager.get_available_tools()

# Get tools from specific server
fs_tools = mcp_manager.get_tools_for_server("filesystem")

# Get tool descriptions
description = mcp_manager.get_tools_description()

# Execute a tool
result = await mcp_manager.execute_tool(
    tool_name="filesystem_read_file",
    arguments={"path": "file.txt"}
)
```

### Configuration

```python
# List configured servers
servers = mcp_manager.list_configured_servers()

# Enable/disable server
mcp_manager.enable_server("github")
mcp_manager.disable_server("slack")

# Add new server
from src.mcp.config import MCPServerConfig

new_server = MCPServerConfig(
    name="my-server",
    command="python",
    args=["server.py"],
    enabled=True
)
mcp_manager.add_server_config(new_server)
```

## Integration with Agents

### Update Supervisor for MCP

Modify `src/agents/supervisor_agent.py`:

```python
def _get_system_prompt(self):
    return """...

Available Agents:
- email_agent: Email operations
- calendar_agent: Calendar management
- idea_agent: Note taking
- mcp_agent: MCP tools (files, web, external services)

Decision Rules:
- If query needs file access → mcp_agent
- If query needs web search → mcp_agent
- If query needs external service → mcp_agent
...
"""
```

### Add MCP to Agent Graph

```python
# In agent_graph.py
def _build_graph(self):
    workflow.add_node("mcp_agent", self.mcp_node)

    workflow.add_conditional_edges(
        "supervisor",
        self.route_to_agent,
        {
            # ... existing routes
            "mcp_agent": "mcp_agent",
        }
    )

    workflow.add_edge("mcp_agent", "supervisor")
```

## Streamlit UI with MCP

Update `src/ui/streamlit_app.py`:

```python
import asyncio
from src.mcp.manager import initialize_mcp

# Initialize MCP
@st.cache_resource
def init_mcp():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    mcp_manager = loop.run_until_complete(
        initialize_mcp(auto_connect=False)
    )
    return mcp_manager

mcp_manager = init_mcp()

# Sidebar - MCP Controls
with st.sidebar:
    st.subheader("MCP Servers")

    configured = mcp_manager.list_configured_servers()
    for server in configured:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(server["name"])
        with col2:
            if st.button("Connect", key=f"connect_{server['name']}"):
                asyncio.run(
                    mcp_manager.connect_server_by_name(server["name"])
                )
                st.success(f"Connected to {server['name']}")
```

## Best Practices

### 1. Security

- **Validate inputs**: Always validate tool arguments
- **Restrict access**: Use BASE_DIR in filesystem server
- **Environment variables**: Store API keys in .env
- **Audit logging**: Log all tool executions

### 2. Error Handling

```python
try:
    result = await mcp_manager.execute_tool(tool_name, args)
    if not result.get("success"):
        logger.error(f"Tool failed: {result.get('error')}")
except Exception as e:
    logger.exception(f"Tool execution error: {e}")
```

### 3. Performance

- **Connection pooling**: Reuse server connections
- **Caching**: Cache tool results when appropriate
- **Async operations**: Use async for all MCP operations
- **Timeout handling**: Set timeouts for tool execution

### 4. Tool Naming

- Use clear, descriptive names
- Prefix with server name: `filesystem_read_file`
- Follow consistent conventions
- Document all parameters

## Troubleshooting

### Server Connection Issues

```python
# Check server status
info = mcp_manager.get_server_info("filesystem")
print(info)

# Reconnect
await mcp_manager.disconnect_server("filesystem")
await mcp_manager.connect_server_by_name("filesystem")
```

### Tool Not Found

```python
# List available tools
tools = mcp_manager.get_available_tools()
for tool in tools:
    print(f"{tool.name}: {tool.description}")

# Check server connection
if "filesystem" not in mcp_manager.get_connected_servers():
    await mcp_manager.connect_server_by_name("filesystem")
```

### npm MCP Servers

For npm-based servers, ensure Node.js is installed:

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Test npx
npx -y @modelcontextprotocol/server-brave-search --help
```

## Examples

### Example 1: File Operations

```python
# Read file
result = await mcp_manager.execute_tool(
    "filesystem_read_file",
    {"path": "README.md"}
)

# Write file
result = await mcp_manager.execute_tool(
    "filesystem_write_file",
    {
        "path": "output.txt",
        "content": "Hello MCP!"
    }
)

# List directory
result = await mcp_manager.execute_tool(
    "filesystem_list_directory",
    {"path": "."}
)
```

### Example 2: Web Search

```python
# Connect to web search server
await mcp_manager.connect_server_by_name("web-search")

# Search
result = await mcp_manager.execute_tool(
    "web-search_search",
    {
        "query": "Model Context Protocol",
        "count": 5
    }
)
```

### Example 3: GitHub Operations

```python
# Connect to GitHub
await mcp_manager.connect_server_by_name("github")

# List repositories
result = await mcp_manager.execute_tool(
    "github_list_repos",
    {"owner": "username"}
)

# Get file content
result = await mcp_manager.execute_tool(
    "github_get_file",
    {
        "owner": "username",
        "repo": "repo-name",
        "path": "README.md"
    }
)
```

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [AgentAru MCP Examples](../src/mcp/servers/)

## Next Steps

1. **Try built-in filesystem server**
2. **Add web search with Brave API**
3. **Create custom MCP server for your use case**
4. **Integrate with existing agents**
5. **Explore official MCP server catalog**
