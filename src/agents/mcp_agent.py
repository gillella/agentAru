"""
MCP-Enhanced Agent

Agent that uses MCP tools for extended functionality.
"""

import asyncio
from typing import Dict, Any, List
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
import logging

from src.core.state import AgentState
from src.core.model_manager import ModelManager
from src.memory.memory_manager import AgentMemoryManager
from src.mcp_integration.client import MCPClient
from src.mcp_integration.tool_manager import MCPToolManager

logger = logging.getLogger(__name__)


class MCPAgent:
    """Agent with MCP tool capabilities"""

    def __init__(
        self,
        model_manager: ModelManager,
        memory_manager: AgentMemoryManager,
        mcp_client: MCPClient,
        mcp_tool_manager: MCPToolManager
    ):
        self.model_manager = model_manager
        self.memory_manager = memory_manager
        self.mcp_client = mcp_client
        self.mcp_tool_manager = mcp_tool_manager
        self.llm = model_manager.get_model()

    def process(self, state: AgentState) -> AgentState:
        """Process with MCP tools (sync wrapper)"""
        # Run async process in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.aprocess(state))

    async def aprocess(self, state: AgentState) -> AgentState:
        """Process with MCP tools (async)"""

        try:
            user_query = state["user_query"]

            # Get relevant memories
            memories = self.memory_manager.search_memories(
                query=user_query,
                limit=3
            )

            # Get available MCP tools
            mcp_tools = self.mcp_tool_manager.get_tools()

            # Build context with tool descriptions
            context = self._build_context(user_query, memories, mcp_tools)

            # Get LLM with tools bound
            if mcp_tools:
                llm_with_tools = self.llm.bind_tools(mcp_tools)
            else:
                llm_with_tools = self.llm

            # Get response
            response = llm_with_tools.invoke([
                SystemMessage(content=context),
                *state["messages"]
            ])

            # Process tool calls if any
            tool_results = []
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    result = await self._execute_mcp_tool(tool_call)
                    tool_results.append(result)

            # Update state
            state["mcp_results"] = {
                "status": "processed",
                "message": response.content,
                "tool_results": tool_results
            }
            state["agent_history"].append("mcp_agent")
            state["messages"].append(AIMessage(content=response.content))
            state["next_agent"] = ""  # Return to supervisor

            logger.info("MCP agent processed successfully")
            return state

        except Exception as e:
            logger.error(f"MCP agent processing failed: {e}")
            state["errors"].append(f"MCP agent error: {str(e)}")
            state["next_agent"] = ""
            return state

    async def _execute_mcp_tool(self, tool_call: Dict) -> Dict[str, Any]:
        """Execute an MCP tool call"""
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})

        try:
            # Find which server has this tool
            for server_name in self.mcp_client.get_connected_servers():
                server_tools = await self.mcp_client.list_tools(server_name)
                tool_names = [t.name for t in server_tools]

                if tool_name in tool_names or tool_name.replace(f"{server_name}_", "") in tool_names:
                    # Execute the tool
                    actual_tool_name = tool_name.replace(f"{server_name}_", "")
                    result = await self.mcp_client.call_tool(
                        server_name=server_name,
                        tool_name=actual_tool_name,
                        arguments=tool_args
                    )

                    return {
                        "tool": tool_name,
                        "result": result,
                        "server": server_name
                    }

            return {
                "tool": tool_name,
                "error": "Tool not found in any connected server"
            }

        except Exception as e:
            logger.error(f"Error executing MCP tool {tool_name}: {e}")
            return {
                "tool": tool_name,
                "error": str(e)
            }

    def _build_context(
        self,
        query: str,
        memories: List[Dict],
        tools: List[Any]
    ) -> str:
        """Build context for MCP agent"""

        memory_text = "\n".join([
            f"- {m.get('memory', '')}" for m in memories
        ])

        tool_descriptions = []
        for tool in tools:
            tool_descriptions.append(
                f"- {tool.name}: {tool.description}"
            )

        tools_text = "\n".join(tool_descriptions) if tool_descriptions else "No tools available"

        return f"""You are AgentAru's MCP-enhanced agent with access to external tools.

Relevant Context:
{memory_text if memory_text else "No relevant memories."}

Available Tools via MCP:
{tools_text}

Current request: {query}

You can use the available MCP tools to complete tasks. Call tools when needed to:
- Access files and directories
- Search the web
- Interact with external services
- Retrieve or store data

Provide a helpful response, using tools as appropriate."""
