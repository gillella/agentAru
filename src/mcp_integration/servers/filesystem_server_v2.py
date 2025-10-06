#!/usr/bin/env python3
"""
MCP Filesystem Server (Updated for MCP SDK v1.16.0)

Provides file system access tools via MCP protocol using FastMCP.
"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("filesystem-server")

# Allowed base directory (for security)
BASE_DIR = Path.cwd()


@mcp.tool()
def read_file(path: str) -> str:
    """
    Read contents of a file

    Args:
        path: Path to the file to read (relative to current directory)
    """
    file_path = BASE_DIR / path

    if not file_path.exists():
        return f"Error: File not found: {path}"

    if not file_path.is_file():
        return f"Error: Not a file: {path}"

    try:
        content = file_path.read_text()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """
    Write content to a file

    Args:
        path: Path to the file to write
        content: Content to write to the file
    """
    file_path = BASE_DIR / path

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool()
def list_directory(path: str = ".") -> str:
    """
    List contents of a directory

    Args:
        path: Path to the directory (default: current directory)
    """
    dir_path = BASE_DIR / path

    if not dir_path.exists():
        return f"Error: Directory not found: {path}"

    if not dir_path.is_dir():
        return f"Error: Not a directory: {path}"

    try:
        items = []
        for item in sorted(dir_path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            items.append(f"{item_type}: {item.name}")

        return "\n".join(items) if items else "Empty directory"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@mcp.tool()
def create_directory(path: str) -> str:
    """
    Create a new directory

    Args:
        path: Path for the new directory
    """
    dir_path = BASE_DIR / path

    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return f"Successfully created directory: {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


if __name__ == "__main__":
    # Run the server
    mcp.run()
