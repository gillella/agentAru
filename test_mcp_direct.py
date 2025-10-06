#!/usr/bin/env python3
"""Direct test of MCP filesystem server connection"""

import asyncio
import sys
from mcp import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession

async def test_server():
    """Test connecting to the MCP server"""

    print("Testing MCP filesystem server connection...")
    print("-" * 60)

    # Server parameters
    server_params = StdioServerParameters(
        command="python3",  # Use python3 explicitly
        args=["src/mcp_integration/servers/filesystem_server_v2.py"],
        env=None
    )

    try:
        print("Starting MCP server...")
        async with stdio_client(server_params) as (read, write):
            print("✅ Server process started")

            async with ClientSession(read, write) as session:
                print("✅ Client session created")

                # Initialize the session
                await session.initialize()
                print("✅ Session initialized")

                # List available tools
                tools_result = await session.list_tools()
                print(f"\n✅ Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Test list_directory tool
                print("\n📂 Testing list_directory tool...")
                result = await session.call_tool("list_directory", arguments={"path": "."})

                if result.content:
                    print("✅ Tool execution successful!")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            # Show first 500 chars
                            text = content.text[:500]
                            print(f"\nResult:\n{text}")
                            if len(content.text) > 500:
                                print(f"... ({len(content.text) - 500} more characters)")
                else:
                    print("⚠️  No content in result")

                print("\n" + "=" * 60)
                print("✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_server())
