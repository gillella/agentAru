# MCP Servers

This directory contains MCP (Model Context Protocol) server implementations for AgentAru.

## Built-in Servers

### Filesystem Server ✅

**File:** `filesystem_server.py`

Provides file system access tools.

**Tools:**
- `read_file` - Read contents of a file
- `write_file` - Write content to a file
- `list_directory` - List contents of a directory
- `create_directory` - Create a new directory

**Usage:**
```bash
# Run directly
python src/mcp/servers/filesystem_server.py

# Or via MCP Manager
python src/main_mcp.py
You: mcp connect filesystem
```

**Security:**
- BASE_DIR restriction to prevent path traversal
- Input validation on all paths
- Error handling for file operations

## Creating Custom MCP Servers

### Template

```python
#!/usr/bin/env python3
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

# Initialize server
app = Server("my-custom-server")

# Define tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="my_tool",
            description="Description of what it does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param"]
            }
        )
    ]

# Implement tool handlers
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "my_tool":
        param = arguments.get("param")

        # Your logic here
        result = f"Processed: {param}"

        return [TextContent(
            type="text",
            text=result
        )]

    return [TextContent(
        type="text",
        text=f"Unknown tool: {name}"
    )]

# Main entry point
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Register Custom Server

Add to `src/mcp/mcp_servers.yaml`:

```yaml
servers:
  - name: my-custom-server
    command: python
    args:
      - src/mcp/servers/my_custom_server.py
    enabled: true
    description: My custom MCP server
    auto_connect: false
```

## Official MCP Servers (npm-based)

These servers are available via npm and configured in `mcp_servers.yaml`:

### Web Search (Brave)
```yaml
name: web-search
command: npx
args: ['-y', '@modelcontextprotocol/server-brave-search']
env:
  BRAVE_API_KEY: 'your-key'
```

### GitHub
```yaml
name: github
command: npx
args: ['-y', '@modelcontextprotocol/server-github']
env:
  GITHUB_TOKEN: 'your-token'
```

### SQLite
```yaml
name: sqlite
command: npx
args: ['-y', '@modelcontextprotocol/server-sqlite', '--db-path', './data/db.sqlite']
```

### Slack
```yaml
name: slack
command: npx
args: ['-y', '@modelcontextprotocol/server-slack']
env:
  SLACK_BOT_TOKEN: 'your-token'
  SLACK_TEAM_ID: 'your-team-id'
```

### Google Drive
```yaml
name: google-drive
command: npx
args: ['-y', '@modelcontextprotocol/server-gdrive']
```

## Tool Schema

All MCP tools follow this schema:

```json
{
  "name": "tool_name",
  "description": "What the tool does",
  "inputSchema": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string|number|boolean|object|array",
        "description": "Parameter description"
      }
    },
    "required": ["param_name"]
  }
}
```

## Response Format

Tools return a list of content items:

```python
[
    TextContent(type="text", text="Result text"),
    ImageContent(type="image", data="base64...", mimeType="image/png"),
    EmbeddedResource(type="resource", resource={...})
]
```

## Testing Your Server

### Test Standalone
```bash
# Run server directly
python src/mcp/servers/your_server.py
```

### Test with MCP Inspector
```bash
# Using MCP Inspector (if installed)
npx @modelcontextprotocol/inspector python src/mcp/servers/your_server.py
```

### Test with AgentAru
```python
# In Python
from src.mcp.manager import initialize_mcp

mcp_manager = await initialize_mcp()
await mcp_manager.connect_server_by_name("your-server")
tools = mcp_manager.get_available_tools()
print(tools)
```

## Best Practices

### 1. Error Handling
Always wrap tool logic in try/except:

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        # Tool logic
        result = process(arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### 2. Input Validation
Validate all inputs before processing:

```python
def validate_path(path: str) -> bool:
    # Prevent path traversal
    if ".." in path:
        return False
    # Add more validation
    return True
```

### 3. Security
- Restrict file system access to safe directories
- Validate all user inputs
- Don't expose sensitive information in error messages
- Use environment variables for credentials

### 4. Documentation
Document each tool clearly:
- Name should be descriptive
- Description should explain what it does
- Parameters should have clear descriptions
- Include examples in docstrings

### 5. Testing
Test all tools thoroughly:
- Unit tests for tool functions
- Integration tests with MCP client
- Error case testing

## Examples

### Example: Weather Server

```python
#!/usr/bin/env python3
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import httpx

app = Server("weather-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_weather",
            description="Get current weather for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates"
                    }
                },
                "required": ["location"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather":
        location = arguments.get("location")

        # Call weather API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.weather.com/v1/location/{location}"
            )
            data = response.json()

        return [TextContent(
            type="text",
            text=f"Weather in {location}: {data['description']}, {data['temp']}°C"
        )]

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Example: Database Server

```python
#!/usr/bin/env python3
from mcp.server import Server
from mcp.types import Tool, TextContent
import sqlite3

app = Server("database-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_db",
            description="Execute SQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query"},
                    "params": {"type": "array", "description": "Query parameters"}
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "query_db":
        query = arguments.get("query")
        params = arguments.get("params", [])

        conn = sqlite3.connect("data.db")
        cursor = conn.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        return [TextContent(
            type="text",
            text=str(results)
        )]
```

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [AgentAru MCP Integration](../../docs/mcp_integration.md)

## Contributing

To add a new MCP server:

1. Create server file in this directory
2. Follow the template above
3. Add configuration to `mcp_servers.yaml`
4. Test thoroughly
5. Document in this README
6. Submit PR

## Support

For issues or questions:
- Check the [MCP Integration Guide](../../docs/mcp_integration.md)
- Review examples in this directory
- Open an issue on GitHub
