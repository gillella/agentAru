"""
MCP Integration Manager

High-level manager for MCP integration with AgentAru.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

from src.mcp_integration.client import MCPClient
from src.mcp_integration.tool_manager import MCPToolManager
from src.mcp_integration.config import MCPConfigManager, MCPServerConfig

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages MCP client, servers, and tools"""

    def __init__(self, config_path: str = "src/mcp_integration/mcp_servers.yaml"):
        self.config_manager = MCPConfigManager(config_path)
        self.mcp_client = MCPClient()
        self.tool_manager = MCPToolManager(self.mcp_client)
        self._initialized = False

    async def initialize(self, auto_connect: bool = True):
        """Initialize MCP system and connect to servers"""

        if self._initialized:
            logger.warning("MCP Manager already initialized")
            return

        try:
            logger.info("Initializing MCP Manager...")

            if auto_connect:
                # Connect to auto-connect servers
                servers = self.config_manager.get_auto_connect_servers()

                for server_config in servers:
                    await self.connect_server(server_config)

            self._initialized = True
            logger.info("MCP Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MCP Manager: {e}")
            raise

    async def connect_server(
        self,
        server_config: MCPServerConfig
    ) -> bool:
        """Connect to an MCP server and register its tools"""

        try:
            logger.info(f"Connecting to MCP server: {server_config.name}")

            # Connect to server
            await self.mcp_client.connect_server(
                server_name=server_config.name,
                command=server_config.command,
                args=server_config.args,
                env=server_config.env
            )

            # Register tools
            await self.tool_manager.register_server_tools(
                server_name=server_config.name,
                prefix=server_config.name  # Prefix tools with server name
            )

            logger.info(f"Successfully connected to {server_config.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to {server_config.name}: {e}")
            return False

    async def connect_server_by_name(self, server_name: str) -> bool:
        """Connect to a server by its configured name"""

        server_config = self.config_manager.get_server_config(server_name)

        if not server_config:
            logger.error(f"Server config not found: {server_name}")
            return False

        if not server_config.enabled:
            logger.warning(f"Server is disabled: {server_name}")
            return False

        return await self.connect_server(server_config)

    async def disconnect_server(self, server_name: str):
        """Disconnect from an MCP server"""
        await self.mcp_client.disconnect_server(server_name)

    async def connect_all_enabled(self):
        """Connect to all enabled servers"""
        servers = self.config_manager.get_enabled_servers()

        results = []
        for server_config in servers:
            result = await self.connect_server(server_config)
            results.append({
                "server": server_config.name,
                "success": result
            })

        return results

    def get_available_tools(self) -> List[Any]:
        """Get all available MCP tools"""
        return self.tool_manager.get_tools()

    def get_tools_for_server(self, server_name: str) -> List[Any]:
        """Get tools from a specific server"""
        return self.tool_manager.get_tools(server_name=server_name)

    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names"""
        return self.mcp_client.get_connected_servers()

    def get_server_info(self, server_name: str) -> Dict[str, Any]:
        """Get information about a server"""
        return self.mcp_client.get_server_info(server_name)

    def list_configured_servers(self) -> List[Dict[str, Any]]:
        """List all configured servers"""
        return self.config_manager.list_servers()

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> str:
        """Execute a tool by name"""
        return await self.tool_manager.execute_tool(tool_name, arguments)

    def get_tools_description(self) -> str:
        """Get formatted description of available tools"""
        return self.tool_manager.create_tool_descriptions()

    async def shutdown(self):
        """Shutdown MCP system and close all connections"""
        logger.info("Shutting down MCP Manager...")
        await self.mcp_client.close_all()
        self._initialized = False
        logger.info("MCP Manager shutdown complete")

    def is_initialized(self) -> bool:
        """Check if MCP manager is initialized"""
        return self._initialized

    # Configuration management methods

    def enable_server(self, server_name: str):
        """Enable a server in configuration"""
        self.config_manager.enable_server(server_name)

    def disable_server(self, server_name: str):
        """Disable a server in configuration"""
        self.config_manager.disable_server(server_name)

    def add_server_config(self, server_config: MCPServerConfig):
        """Add a new server configuration"""
        self.config_manager.add_server(server_config)

    def remove_server_config(self, server_name: str):
        """Remove a server configuration"""
        self.config_manager.remove_server(server_name)


# Global MCP manager instance
_mcp_manager: Optional[MCPManager] = None


def get_mcp_manager(config_path: str = "src/mcp_integration/mcp_servers.yaml") -> MCPManager:
    """Get or create global MCP manager instance"""
    global _mcp_manager

    if _mcp_manager is None:
        _mcp_manager = MCPManager(config_path)

    return _mcp_manager


async def initialize_mcp(
    config_path: str = "src/mcp_integration/mcp_servers.yaml",
    auto_connect: bool = True
) -> MCPManager:
    """Initialize and return MCP manager"""
    manager = get_mcp_manager(config_path)

    if not manager.is_initialized():
        await manager.initialize(auto_connect=auto_connect)

    return manager
