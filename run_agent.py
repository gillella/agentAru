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

    # MCP - connect to both filesystem and web-search
    mcp_manager = await initialize_mcp(auto_connect=False)

    fs_success = await mcp_manager.connect_server_by_name("filesystem")
    web_success = await mcp_manager.connect_server_by_name("web-search")

    tools = mcp_manager.tool_manager.get_tools()

    if fs_success:
        print("✅ MCP filesystem server connected")
    if web_success:
        print("✅ MCP web-search server connected")

    print(f"✅ {len(tools)} tools available")

    # Model Manager - bind tools to LLM
    model_manager = ModelManager()
    llm = model_manager.get_model()

    # Bind MCP tools to the LLM
    if tools:
        llm_with_tools = llm.bind_tools(tools)
        print(f"✅ Using model: {settings.default_model} with {len(tools)} tools")
    else:
        llm_with_tools = llm
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
                tools = mcp_manager.tool_manager.get_tools()
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

            # Process with LLM using agentic loop
            print("\n🤖 AgentAru: ", end="", flush=True)

            from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

            # Create message history for this turn
            messages = [HumanMessage(content=user_input)]

            # Agent loop - allow up to 5 iterations
            max_iterations = 5
            response = None
            for iteration in range(max_iterations):
                # Get LLM response
                response = llm_with_tools.invoke(messages)
                messages.append(response)

                # Check if LLM wants to use tools
                if not response.tool_calls:
                    # No tools needed, return final answer
                    print(response.content)
                    break

                # Execute tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    # Execute the tool via MCP
                    try:
                        result = await mcp_manager.execute_tool(tool_name, tool_args)
                        messages.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        ))
                    except Exception as e:
                        messages.append(ToolMessage(
                            content=f"Error executing {tool_name}: {e}",
                            tool_call_id=tool_call["id"]
                        ))
            else:
                # Loop completed without break - print last response
                if response and hasattr(response, 'content'):
                    print(response.content)

            # Store interaction in memory
            try:
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
