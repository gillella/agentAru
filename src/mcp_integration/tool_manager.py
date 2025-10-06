"""
MCP Tool Manager

Manages MCP tools and integrates them with LangChain for agent use.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from langchain.tools import Tool
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from src.mcp_integration.client import MCPClient

logger = logging.getLogger(__name__)


class MCPToolWrapper(BaseTool):
    """LangChain tool wrapper for MCP tools"""

    name: str
    description: str
    mcp_client: Any = Field(exclude=True)
    server_name: str
    tool_name: str
    input_schema: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True

    def _run(self, **kwargs) -> str:
        """Synchronous execution (not supported for MCP)"""
        raise NotImplementedError("MCP tools require async execution")

    async def _arun(self, **kwargs) -> str:
        """Async execution of MCP tool"""
        try:
            result = await self.mcp_client.call_tool(
                server_name=self.server_name,
                tool_name=self.tool_name,
                arguments=kwargs
            )

            if result.get("success"):
                # Extract text content
                if "content" in result:
                    text_parts = []
                    for item in result["content"]:
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                    return "\n".join(text_parts)

                return str(result.get("result", ""))

            return f"Error: {result.get('error', 'Unknown error')}"

        except Exception as e:
            logger.error(f"Error executing MCP tool {self.tool_name}: {e}")
            return f"Error: {str(e)}"


class MCPToolManager:
    """Manages MCP tools and provides them to agents"""

    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.tools_registry: Dict[str, List[BaseTool]] = {}

    async def register_server_tools(
        self,
        server_name: str,
        prefix: str = None
    ) -> List[BaseTool]:
        """
        Register all tools from an MCP server as LangChain tools

        Args:
            server_name: MCP server name
            prefix: Optional prefix for tool names

        Returns:
            List of LangChain tools
        """
        try:
            mcp_tools = await self.mcp_client.list_tools(server_name)

            langchain_tools = []

            for mcp_tool in mcp_tools:
                # Create tool name with optional prefix
                tool_name = f"{prefix}_{mcp_tool.name}" if prefix else mcp_tool.name

                # Create LangChain tool wrapper
                lc_tool = MCPToolWrapper(
                    name=tool_name,
                    description=mcp_tool.description or f"MCP tool: {mcp_tool.name}",
                    mcp_client=self.mcp_client,
                    server_name=server_name,
                    tool_name=mcp_tool.name,
                    input_schema=mcp_tool.inputSchema or {}
                )

                langchain_tools.append(lc_tool)

            # Store in registry
            self.tools_registry[server_name] = langchain_tools

            logger.info(
                f"Registered {len(langchain_tools)} tools from MCP server: {server_name}"
            )

            return langchain_tools

        except Exception as e:
            logger.error(f"Failed to register tools from {server_name}: {e}")
            return []

    def get_tools(
        self,
        server_name: str = None,
        tool_names: List[str] = None
    ) -> List[BaseTool]:
        """
        Get registered tools

        Args:
            server_name: Filter by server name
            tool_names: Filter by specific tool names

        Returns:
            List of tools
        """
        if server_name:
            tools = self.tools_registry.get(server_name, [])
        else:
            # Get all tools from all servers
            tools = []
            for server_tools in self.tools_registry.values():
                tools.extend(server_tools)

        # Filter by tool names if specified
        if tool_names:
            tools = [t for t in tools if t.name in tool_names]

        return tools

    def get_tool_by_name(self, tool_name: str) -> Optional[BaseTool]:
        """Get a specific tool by name"""
        all_tools = self.get_tools()
        for tool in all_tools:
            if tool.name == tool_name:
                return tool
        return None

    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available tools with metadata"""
        tools_info = []

        for server_name, tools in self.tools_registry.items():
            for tool in tools:
                tools_info.append({
                    "server": server_name,
                    "name": tool.name,
                    "description": tool.description,
                    "schema": getattr(tool, 'input_schema', {})
                })

        return tools_info

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """Execute a tool by name"""
        tool = self.get_tool_by_name(tool_name)

        if not tool:
            return f"Error: Tool '{tool_name}' not found"

        try:
            result = await tool._arun(**arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error: {str(e)}"

    def create_tool_descriptions(self) -> str:
        """Create a formatted description of all available tools"""
        tools_info = self.list_available_tools()

        if not tools_info:
            return "No MCP tools available."

        descriptions = ["Available MCP Tools:\n"]

        for tool in tools_info:
            descriptions.append(
                f"- {tool['name']} ({tool['server']}): {tool['description']}"
            )

        return "\n".join(descriptions)

    def get_tools_for_agent(
        self,
        server_names: List[str] = None,
        tool_names: List[str] = None
    ) -> List[BaseTool]:
        """
        Get tools formatted for agent use

        Args:
            server_names: List of server names to include
            tool_names: Specific tool names to include

        Returns:
            List of tools ready for agent binding
        """
        if server_names:
            tools = []
            for server_name in server_names:
                tools.extend(self.get_tools(server_name))
        else:
            tools = self.get_tools()

        if tool_names:
            tools = [t for t in tools if t.name in tool_names]

        return tools
