#!/usr/bin/env python3
"""
AgentAru with MCP Integration - Main Application Entry Point
"""

import os
import asyncio
from dotenv import load_dotenv
import logging

from src.core.model_manager import ModelManager
from src.core.agent_graph import AgentAruGraph
from src.memory.memory_manager import AgentMemoryManager
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.email_agent import EmailAgent
from src.agents.calendar_agent import CalendarAgent
from src.agents.idea_agent import IdeaAgent
from src.agents.mcp_agent import MCPAgent
from src.mcp_integration.manager import initialize_mcp
from src.utils.logger import setup_logger
from src.config.settings import settings

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(level=settings.log_level)


async def initialize_agent() -> AgentAruGraph:
    """Initialize the complete agent system with MCP"""

    logger.info("Initializing AgentAru with MCP integration...")

    # Initialize MCP
    mcp_manager = await initialize_mcp(auto_connect=False)

    # Connect to both filesystem and web-search servers
    await mcp_manager.connect_server_by_name("filesystem")
    await mcp_manager.connect_server_by_name("web-search")

    # Initialize core components
    model_manager = ModelManager()
    memory_manager = AgentMemoryManager(
        user_id="default_user",
        config={"decay_days": settings.memory_decay_days},
    )

    # Create specialized agents
    supervisor = SupervisorAgent(model_manager, memory_manager)
    email_agent = EmailAgent(model_manager, memory_manager)
    calendar_agent = CalendarAgent(model_manager, memory_manager)
    idea_agent = IdeaAgent(model_manager, memory_manager)

    # Create MCP-enhanced agent
    mcp_agent = MCPAgent(
        model_manager,
        memory_manager,
        mcp_manager.mcp_client,
        mcp_manager.tool_manager
    )

    # Build agent graph
    graph = AgentAruGraph(model_manager, memory_manager)
    graph.set_agents(
        supervisor=supervisor,
        email=email_agent,
        calendar=calendar_agent,
        idea=idea_agent,
    )

    # Add MCP agent node
    graph.mcp_agent = mcp_agent

    # Compile graph
    graph.compile()

    logger.info("AgentAru with MCP initialized successfully")

    # Show available MCP tools
    tools_desc = mcp_manager.get_tools_description()
    logger.info(f"\n{tools_desc}")

    return graph, mcp_manager


async def run_cli_async():
    """Run AgentAru with MCP in CLI mode (async)"""

    print("=" * 60)
    print("🤖 AgentAru with MCP - Your Personal AI Assistant")
    print("=" * 60)
    print()

    # Initialize agent
    try:
        agent, mcp_manager = await initialize_agent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        print(f"Error: Failed to initialize agent - {e}")
        return

    print("Agent ready! Type 'exit' to quit, 'mcp' for MCP commands.\n")

    # Main loop
    session_id = f"cli_session_{os.getpid()}"

    try:
        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("Goodbye! 👋")
                    break

                # MCP commands
                if user_input.lower() == "mcp":
                    print("\nMCP Commands:")
                    print("  mcp servers - List connected servers")
                    print("  mcp tools - List available tools")
                    print("  mcp connect <server> - Connect to a server")
                    print()
                    continue

                if user_input.lower() == "mcp servers":
                    servers = mcp_manager.get_connected_servers()
                    print(f"\nConnected servers: {', '.join(servers)}\n")
                    continue

                if user_input.lower() == "mcp tools":
                    print(f"\n{mcp_manager.get_tools_description()}\n")
                    continue

                if user_input.lower().startswith("mcp connect "):
                    server_name = user_input.split(" ", 2)[2]
                    success = await mcp_manager.connect_server_by_name(server_name)
                    if success:
                        print(f"✅ Connected to {server_name}\n")
                    else:
                        print(f"❌ Failed to connect to {server_name}\n")
                    continue

                # Process with agent
                result = agent.run(user_input=user_input, session_id=session_id)

                # Extract and display response
                if result["messages"]:
                    last_message = result["messages"][-1]
                    response = last_message.content
                    print(f"\nAgentAru: {response}\n")

                    # Show agent path if debug mode
                    if settings.debug:
                        agents_used = " → ".join(result.get("agent_history", []))
                        print(f"[Debug] Agents: {agents_used}")
                        print()

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                print(f"\nError: {e}\n")

    finally:
        # Cleanup
        await mcp_manager.shutdown()


def run_cli():
    """Synchronous wrapper for CLI"""
    asyncio.run(run_cli_async())


if __name__ == "__main__":
    run_cli()
