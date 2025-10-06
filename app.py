#!/usr/bin/env python3
"""
AgentAru - Streamlit Web UI
Beautiful interface for your local AI agent
"""

import streamlit as st
import asyncio
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, '/Users/aravindgillella/projects/agentAru')

from src.core.model_manager import ModelManager
from src.mcp_integration.manager import initialize_mcp
from src.memory.memory_manager import AgentMemoryManager
from src.config.settings import settings
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# Page config
st.set_page_config(
    page_title="AgentAru - Local AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .tool-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        background-color: #e1f5fe;
        border-radius: 0.25rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False

if "mcp_manager" not in st.session_state:
    st.session_state.mcp_manager = None

if "llm" not in st.session_state:
    st.session_state.llm = None

if "memory_manager" not in st.session_state:
    st.session_state.memory_manager = None


async def initialize_agent():
    """Initialize all agent components"""
    if st.session_state.agent_initialized:
        return True

    with st.spinner("Initializing agent..."):
        try:
            # MCP
            mcp_manager = await initialize_mcp(auto_connect=False)
            await mcp_manager.connect_server_by_name("filesystem")
            await mcp_manager.connect_server_by_name("web-search")
            st.session_state.mcp_manager = mcp_manager

            # Model
            model_manager = ModelManager()
            llm = model_manager.get_model()

            # Bind MCP tools to LLM
            tools = mcp_manager.tool_manager.get_tools()
            if tools:
                st.session_state.llm = llm.bind_tools(tools)
                st.session_state.llm_no_tools = llm  # Keep original for fallback
            else:
                st.session_state.llm = llm

            # Memory
            st.session_state.memory_manager = AgentMemoryManager(
                user_id="streamlit_user"
            )

            st.session_state.agent_initialized = True
            return True

        except Exception as e:
            st.error(f"Failed to initialize agent: {e}")
            return False


# Header
st.markdown('<div class="main-header">🤖 AgentAru</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your Local AI Agent with MCP Tools</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    # Model info
    st.subheader("🧠 Model")
    st.info(f"**{settings.default_model}**\n\nRunning locally via Ollama")

    # Initialize button
    if not st.session_state.agent_initialized:
        if st.button("🚀 Initialize Agent", type="primary"):
            asyncio.run(initialize_agent())
            if st.session_state.agent_initialized:
                st.success("Agent initialized!")
                st.rerun()
    else:
        st.success("✅ Agent Ready")

        # MCP Tools
        st.subheader("🔧 MCP Tools")
        if st.session_state.mcp_manager:
            tools = st.session_state.mcp_manager.tool_manager.get_tools()
            st.write(f"**{len(tools)} tools available:**")
            for tool in tools:
                # Extract just the tool name (remove server prefix if present)
                display_name = tool.name.replace('filesystem_', '').replace('web_', '').replace('_', ' ').title()
                st.markdown(f"- `{display_name}`")
                with st.expander(f"ℹ️ {display_name} details", expanded=False):
                    st.write(f"**Full name:** `{tool.name}`")
                    st.write(f"**Description:** {tool.description}")

        # Memory stats
        st.subheader("🧠 Memory")
        st.info("Using local Ollama embeddings\n- Nomic-embed-text\n- Qdrant vector store")

        # Actions
        st.subheader("Actions")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        if st.button("💾 View Memories"):
            st.session_state.show_memories = True

# Main chat area
if not st.session_state.agent_initialized:
    st.warning("👈 Click 'Initialize Agent' in the sidebar to get started")
    st.info("""
    **AgentAru Features:**
    - 🏠 100% Local LLM (Qwen2.5 7B)
    - 🧠 Local Memory (Ollama embeddings)
    - 🔧 MCP Filesystem Tools
    - 🚫 No cloud API keys needed
    """)
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    from langchain_core.messages import ToolMessage

                    # Agent loop
                    messages = [HumanMessage(content=prompt)]
                    max_iterations = 5

                    for iteration in range(max_iterations):
                        response = st.session_state.llm.invoke(messages)
                        messages.append(response)

                        # Check if tools were called
                        if not response.tool_calls:
                            # No tools, final answer ready
                            response_text = response.content
                            break

                        # Execute tool calls
                        with st.spinner("Using tools..."):
                            for tool_call in response.tool_calls:
                                tool_name = tool_call["name"]
                                tool_args = tool_call["args"]

                                try:
                                    # Execute tool asynchronously
                                    result = asyncio.run(
                                        st.session_state.mcp_manager.execute_tool(
                                            tool_name, tool_args
                                        )
                                    )
                                    messages.append(ToolMessage(
                                        content=str(result),
                                        tool_call_id=tool_call["id"]
                                    ))
                                except Exception as e:
                                    messages.append(ToolMessage(
                                        content=f"Error: {e}",
                                        tool_call_id=tool_call["id"]
                                    ))

                    st.markdown(response_text)

                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text
                    })

                    # Store in memory (async, non-blocking)
                    try:
                        st.session_state.memory_manager.add_interaction([
                            HumanMessage(content=prompt),
                            AIMessage(content=response_text)
                        ])
                    except:
                        pass

                except Exception as e:
                    st.error(f"Error: {e}")

# Show memories sidebar (if requested)
if st.session_state.get("show_memories", False):
    with st.sidebar:
        st.subheader("💭 Recent Memories")
        if st.session_state.memory_manager:
            try:
                memories = st.session_state.memory_manager.search_memories(
                    "recent conversation",
                    limit=5
                )
                if memories:
                    for i, mem in enumerate(memories, 1):
                        st.text(f"{i}. {mem.get('memory', 'N/A')[:60]}...")
                else:
                    st.info("No memories yet")
            except:
                st.info("Memory search not available")

        if st.button("Close"):
            st.session_state.show_memories = False
            st.rerun()
