"""
MCP Server Configuration

Manages MCP server configurations and connection settings.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
import yaml
import os


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server"""

    name: str
    command: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    enabled: bool = True
    description: Optional[str] = None
    auto_connect: bool = False


class MCPConfig(BaseModel):
    """Overall MCP configuration"""

    servers: List[MCPServerConfig] = Field(default_factory=list)


class MCPConfigManager:
    """Manages MCP server configurations"""

    def __init__(self, config_path: str = "src/mcp_integration/mcp_servers.yaml"):
        self.config_path = Path(config_path)
        self.config: MCPConfig = MCPConfig()
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            # Create default config
            self._create_default_config()
            return

        try:
            with open(self.config_path) as f:
                config_data = yaml.safe_load(f)

            if config_data and "servers" in config_data:
                servers = [
                    MCPServerConfig(**server_data)
                    for server_data in config_data["servers"]
                ]
                self.config = MCPConfig(servers=servers)

        except Exception as e:
            print(f"Error loading MCP config: {e}")
            self._create_default_config()

    def _create_default_config(self):
        """Create default MCP server configuration"""
        default_servers = [
            MCPServerConfig(
                name="filesystem",
                command="python",
                args=["src/mcp/servers/filesystem_server.py"],
                description="File system access tools",
                enabled=True,
                auto_connect=False
            ),
            MCPServerConfig(
                name="web-search",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-brave-search"],
                env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")},
                description="Web search via Brave Search API",
                enabled=False,
                auto_connect=False
            ),
            MCPServerConfig(
                name="github",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")},
                description="GitHub repository access",
                enabled=False,
                auto_connect=False
            ),
            MCPServerConfig(
                name="sqlite",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-sqlite"],
                description="SQLite database access",
                enabled=False,
                auto_connect=False
            )
        ]

        self.config = MCPConfig(servers=default_servers)
        self._save_config()

    def _save_config(self):
        """Save configuration to YAML file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            config_dict = {
                "servers": [
                    {
                        "name": server.name,
                        "command": server.command,
                        "args": server.args,
                        "env": server.env,
                        "enabled": server.enabled,
                        "description": server.description,
                        "auto_connect": server.auto_connect
                    }
                    for server in self.config.servers
                ]
            }

            with open(self.config_path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)

        except Exception as e:
            print(f"Error saving MCP config: {e}")

    def get_enabled_servers(self) -> List[MCPServerConfig]:
        """Get list of enabled servers"""
        return [s for s in self.config.servers if s.enabled]

    def get_auto_connect_servers(self) -> List[MCPServerConfig]:
        """Get servers that should auto-connect"""
        return [s for s in self.config.servers if s.enabled and s.auto_connect]

    def get_server_config(self, name: str) -> Optional[MCPServerConfig]:
        """Get configuration for a specific server"""
        for server in self.config.servers:
            if server.name == name:
                return server
        return None

    def add_server(self, server_config: MCPServerConfig):
        """Add a new server configuration"""
        self.config.servers.append(server_config)
        self._save_config()

    def remove_server(self, name: str):
        """Remove a server configuration"""
        self.config.servers = [
            s for s in self.config.servers if s.name != name
        ]
        self._save_config()

    def enable_server(self, name: str):
        """Enable a server"""
        server = self.get_server_config(name)
        if server:
            server.enabled = True
            self._save_config()

    def disable_server(self, name: str):
        """Disable a server"""
        server = self.get_server_config(name)
        if server:
            server.enabled = False
            self._save_config()

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all configured servers"""
        return [
            {
                "name": s.name,
                "description": s.description,
                "enabled": s.enabled,
                "auto_connect": s.auto_connect,
                "command": s.command
            }
            for s in self.config.servers
        ]
