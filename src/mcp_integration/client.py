"""
MCP (Model Context Protocol) Client Integration

Provides connection and interaction with MCP servers for standardized tool access.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for connecting to MCP servers"""

    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.tools: Dict[str, List[Tool]] = {}
        self.server_configs: Dict[str, Dict[str, Any]] = {}
        self._stdio_contexts: Dict[str, Any] = {}  # Store stdio context managers
        self._session_contexts: Dict[str, Any] = {}  # Store session context managers

    async def connect_server(
        self,
        server_name: str,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None
    ) -> ClientSession:
        """
        Connect to an MCP server

        Args:
            server_name: Unique name for this server
            command: Command to run the server
            args: Command arguments
            env: Environment variables

        Returns:
            ClientSession instance
        """
        try:
            server_params = StdioServerParameters(
                command=command,
                args=args or [],
                env=env
            )

            # Store config for reconnection
            self.server_configs[server_name] = {
                "command": command,
                "args": args,
                "env": env
            }

            logger.info(f"Connecting to MCP server: {server_name}")

            # Create and enter stdio context
            stdio_ctx = stdio_client(server_params)
            read, write = await stdio_ctx.__aenter__()
            self._stdio_contexts[server_name] = stdio_ctx

            # Create and enter session context
            session_ctx = ClientSession(read, write)
            session = await session_ctx.__aenter__()
            self._session_contexts[server_name] = session_ctx

            # Initialize session
            await session.initialize()

            # Store session
            self.sessions[server_name] = session

            # List and cache tools
            tools_result = await session.list_tools()
            self.tools[server_name] = tools_result.tools

            logger.info(
                f"Connected to {server_name}: {len(self.tools[server_name])} tools available"
            )

            return session

        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            raise

    async def disconnect_server(self, server_name: str):
        """Disconnect from an MCP server"""
        if server_name in self.sessions:
            try:
                # Exit session context
                if server_name in self._session_contexts:
                    await self._session_contexts[server_name].__aexit__(None, None, None)
                    del self._session_contexts[server_name]

                # Exit stdio context
                if server_name in self._stdio_contexts:
                    await self._stdio_contexts[server_name].__aexit__(None, None, None)
                    del self._stdio_contexts[server_name]

                # Clean up session and tools
                del self.sessions[server_name]
                if server_name in self.tools:
                    del self.tools[server_name]

                logger.info(f"Disconnected from MCP server: {server_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {e}")

    async def list_tools(self, server_name: str = None) -> List[Tool]:
        """
        List available tools from MCP servers

        Args:
            server_name: Specific server name, or None for all servers

        Returns:
            List of Tool objects
        """
        if server_name:
            return self.tools.get(server_name, [])

        # Return tools from all servers
        all_tools = []
        for tools in self.tools.values():
            all_tools.extend(tools)
        return all_tools

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any] = None
    ) -> Any:
        """
        Call an MCP tool

        Args:
            server_name: Server providing the tool
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if server_name not in self.sessions:
            raise ValueError(f"Not connected to server: {server_name}")

        session = self.sessions[server_name]

        try:
            logger.debug(f"Calling MCP tool: {server_name}/{tool_name}")

            result = await session.call_tool(
                tool_name,
                arguments=arguments or {}
            )

            # Extract content from result
            if hasattr(result, 'content'):
                content_items = []
                for item in result.content:
                    if isinstance(item, TextContent):
                        content_items.append({
                            "type": "text",
                            "text": item.text
                        })
                    elif isinstance(item, ImageContent):
                        content_items.append({
                            "type": "image",
                            "data": item.data,
                            "mimeType": item.mimeType
                        })
                    elif isinstance(item, EmbeddedResource):
                        content_items.append({
                            "type": "resource",
                            "resource": item.resource
                        })

                return {
                    "success": True,
                    "content": content_items,
                    "isError": getattr(result, 'isError', False)
                }

            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def read_resource(
        self,
        server_name: str,
        uri: str
    ) -> Optional[str]:
        """
        Read a resource from MCP server

        Args:
            server_name: Server name
            uri: Resource URI

        Returns:
            Resource content
        """
        if server_name not in self.sessions:
            raise ValueError(f"Not connected to server: {server_name}")

        session = self.sessions[server_name]

        try:
            result = await session.read_resource(uri)

            if hasattr(result, 'contents'):
                # Combine all text content
                text_parts = []
                for content in result.contents:
                    if isinstance(content, TextContent):
                        text_parts.append(content.text)

                return "\n".join(text_parts)

            return None

        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return None

    async def list_resources(
        self,
        server_name: str
    ) -> List[Dict[str, Any]]:
        """List available resources from an MCP server"""
        if server_name not in self.sessions:
            raise ValueError(f"Not connected to server: {server_name}")

        session = self.sessions[server_name]

        try:
            result = await session.list_resources()

            resources = []
            for resource in result.resources:
                resources.append({
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": getattr(resource, 'description', None),
                    "mimeType": getattr(resource, 'mimeType', None)
                })

            return resources

        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return []

    async def get_tool_schema(
        self,
        server_name: str,
        tool_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get the JSON schema for a specific tool"""
        tools = await self.list_tools(server_name)

        for tool in tools:
            if tool.name == tool_name:
                return {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }

        return None

    async def close_all(self):
        """Close all MCP server connections"""
        for server_name in list(self.sessions.keys()):
            await self.disconnect_server(server_name)

    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names"""
        return list(self.sessions.keys())

    def get_server_info(self, server_name: str) -> Dict[str, Any]:
        """Get information about a connected server"""
        if server_name not in self.sessions:
            return {}

        return {
            "name": server_name,
            "connected": True,
            "tools_count": len(self.tools.get(server_name, [])),
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in self.tools.get(server_name, [])
            ],
            "config": self.server_configs.get(server_name, {})
        }
