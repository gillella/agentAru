#!/usr/bin/env python3
"""
AgentAru - Main Application Entry Point
"""

import os
from dotenv import load_dotenv
import logging

from src.core.model_manager import ModelManager
from src.core.agent_graph import AgentAruGraph
from src.memory.memory_manager import AgentMemoryManager
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.email_agent import EmailAgent
from src.agents.calendar_agent import CalendarAgent
from src.agents.idea_agent import IdeaAgent
from src.utils.logger import setup_logger
from src.config.settings import settings

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(level=settings.log_level)


def initialize_agent() -> AgentAruGraph:
    """Initialize the complete agent system"""

    logger.info("Initializing AgentAru system...")

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

    # Build agent graph
    graph = AgentAruGraph(model_manager, memory_manager)
    graph.set_agents(
        supervisor=supervisor,
        email=email_agent,
        calendar=calendar_agent,
        idea=idea_agent,
    )

    # Compile graph
    graph.compile()

    logger.info("AgentAru system initialized successfully")
    return graph


def run_cli():
    """Run AgentAru in CLI mode"""

    print("=" * 60)
    print("🤖 AgentAru - Your Personal AI Assistant")
    print("=" * 60)
    print()

    # Initialize agent
    try:
        agent = initialize_agent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        print(f"Error: Failed to initialize agent - {e}")
        return

    print("Agent ready! Type 'exit' to quit.\n")

    # Main loop
    session_id = f"cli_session_{os.getpid()}"

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye! 👋")
                break

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


if __name__ == "__main__":
    run_cli()
