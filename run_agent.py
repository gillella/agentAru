#!/usr/bin/env python3
"""
Interactive CLI for AgentAru with Local LLM
"""

import asyncio
import sys
from dotenv import load_dotenv

sys.path.insert(0, '/Users/aravindgillella/projects/agentAru')

from src.core.model_manager import ModelManager
from src.mcp_integration.manager import initialize_mcp
from src.memory.memory_manager import AgentMemoryManager
from src.config.settings import settings

load_dotenv()


async def run_interactive():
    """Run AgentAru in interactive mode"""

    print("=" * 60)
    print("🤖 AgentAru - Local LLM Agent")
    print("=" * 60)
    print()

    # Initialize components
    print("Initializing agent...")

    # MCP
    mcp_manager = await initialize_mcp(auto_connect=False)
    success = await mcp_manager.connect_server_by_name("filesystem")

    if success:
        print("✅ MCP filesystem server connected")
        tools = mcp_manager.tool_manager.get_all_tools()
        print(f"✅ {len(tools)} tools available")
    else:
        print("⚠️  MCP server not connected")

    # Model Manager
    model_manager = ModelManager()
    llm = model_manager.get_model()
    print(f"✅ Using model: {settings.default_model}")

    # Memory
    memory_manager = AgentMemoryManager(user_id="interactive_user")
    print("✅ Memory system initialized")

    print()
    print("Agent ready! Type your questions or commands.")
    print("Special commands:")
    print("  'mcp list' - Show available MCP tools")
    print("  'memory' - Search your conversation history")
    print("  'exit' - Quit")
    print()

    # Main loop
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye!")
                break

            # Special commands
            if user_input.lower() == "mcp list":
                tools = mcp_manager.tool_manager.get_all_tools()
                print(f"\n📦 Available MCP Tools ({len(tools)}):")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:60]}")
                continue

            if user_input.lower().startswith("memory"):
                query = user_input[6:].strip() or "recent"
                memories = memory_manager.search_memories(query, limit=3)
                print(f"\n🧠 Found {len(memories)} memories:")
                for i, mem in enumerate(memories, 1):
                    print(f"  {i}. {mem.get('memory', 'N/A')[:80]}...")
                continue

            # Process with LLM
            print("\n🤖 AgentAru: ", end="", flush=True)

            # For now, simple direct LLM call
            # TODO: Later integrate with full agent graph
            response = llm.invoke(user_input)
            print(response.content)

            # Store interaction in memory (async, don't wait)
            try:
                from langchain_core.messages import HumanMessage, AIMessage
                memory_manager.add_interaction([
                    HumanMessage(content=user_input),
                    AIMessage(content=response.content)
                ])
            except Exception as e:
                # Silently fail on memory storage
                pass

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

    # Cleanup
    await mcp_manager.shutdown()
    print("\nSession ended.")


if __name__ == "__main__":
    asyncio.run(run_interactive())
