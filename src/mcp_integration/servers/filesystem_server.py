#!/usr/bin/env python3
"""
MCP Filesystem Server

Provides file system access tools via MCP protocol.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("filesystem-server")

# Allowed base directory (for security)
BASE_DIR = Path.cwd()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available filesystem tools"""
    return [
        Tool(
            name="read_file",
            description="Read contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="create_directory",
            description="Create a new directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path for the new directory"
                    }
                },
                "required": ["path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    try:
        if name == "read_file":
            return await read_file(arguments.get("path"))

        elif name == "write_file":
            return await write_file(
                arguments.get("path"),
                arguments.get("content")
            )

        elif name == "list_directory":
            return await list_directory(arguments.get("path"))

        elif name == "create_directory":
            return await create_directory(arguments.get("path"))

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def read_file(path: str) -> list[TextContent]:
    """Read file contents"""
    file_path = BASE_DIR / path

    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"File not found: {path}"
        )]

    if not file_path.is_file():
        return [TextContent(
            type="text",
            text=f"Not a file: {path}"
        )]

    try:
        content = file_path.read_text()
        return [TextContent(
            type="text",
            text=content
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error reading file: {str(e)}"
        )]


async def write_file(path: str, content: str) -> list[TextContent]:
    """Write content to file"""
    file_path = BASE_DIR / path

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

        return [TextContent(
            type="text",
            text=f"Successfully wrote to {path}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error writing file: {str(e)}"
        )]


async def list_directory(path: str) -> list[TextContent]:
    """List directory contents"""
    dir_path = BASE_DIR / path

    if not dir_path.exists():
        return [TextContent(
            type="text",
            text=f"Directory not found: {path}"
        )]

    if not dir_path.is_dir():
        return [TextContent(
            type="text",
            text=f"Not a directory: {path}"
        )]

    try:
        items = []
        for item in sorted(dir_path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            items.append(f"{item_type}: {item.name}")

        return [TextContent(
            type="text",
            text="\n".join(items) if items else "Empty directory"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error listing directory: {str(e)}"
        )]


async def create_directory(path: str) -> list[TextContent]:
    """Create a new directory"""
    dir_path = BASE_DIR / path

    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return [TextContent(
            type="text",
            text=f"Successfully created directory: {path}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error creating directory: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    logger.info("Starting Filesystem MCP Server...")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
