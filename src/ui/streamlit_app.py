import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.model_manager import ModelManager
from src.core.agent_graph import AgentAruGraph
from src.memory.memory_manager import AgentMemoryManager
from src.agents.supervisor_agent import SupervisorAgent
from src.agents.email_agent import EmailAgent
from src.agents.calendar_agent import CalendarAgent
from src.agents.idea_agent import IdeaAgent
from src.config.settings import settings

# Page config
st.set_page_config(
    page_title="AgentAru - Your AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().timestamp()}"
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False


init_session_state()


# Initialize components
@st.cache_resource
def initialize_agent():
    """Initialize the agent system"""
    model_manager = ModelManager()
    memory_manager = AgentMemoryManager(
        user_id="streamlit_user",
        config={"decay_days": settings.memory_decay_days},
    )

    # Create specialized agents
    supervisor = SupervisorAgent(model_manager, memory_manager)
    email_agent = EmailAgent(model_manager, memory_manager)
    calendar_agent = CalendarAgent(model_manager, memory_manager)
    idea_agent = IdeaAgent(model_manager, memory_manager)

    # Build agent graph
    graph = AgentAruGraph(model_manager, memory_manager, user_id="streamlit_user")
    graph.set_agents(
        supervisor=supervisor,
        email=email_agent,
        calendar=calendar_agent,
        idea=idea_agent,
    )

    graph.compile()
    return graph, model_manager, memory_manager


try:
    agent, model_manager, memory_manager = initialize_agent()
    st.session_state.agent_initialized = True
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()


# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")

    # Model selection
    st.subheader("Model Configuration")

    available_models = model_manager.list_models()
    model_options = [
        f"{m.display_name} ({m.name})" for m in available_models if not m.local
    ]
    local_model_options = [
        f"{m.display_name} ({m.name})" for m in available_models if m.local
    ]

    model_choice = st.selectbox(
        "Select Model",
        options=model_options + ["---"] + local_model_options,
        index=0,
    )

    if st.button("Switch Model"):
        # Extract model name from display
        model_name = model_choice.split("(")[1].rstrip(")")
        try:
            model_manager.switch_model(model_name)
            st.success(f"Switched to {model_name}")
        except Exception as e:
            st.error(f"Failed to switch model: {e}")

    # Memory controls
    st.subheader("Memory Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("View Memories"):
            memories = memory_manager.get_all_memories()
            st.json(memories[:10] if len(memories) > 10 else memories)

    with col2:
        if st.button("Clear Session"):
            st.session_state.messages = []
            st.rerun()

    # Statistics
    st.subheader("Statistics")
    st.metric("Messages", len(st.session_state.messages))
    st.metric("Session ID", st.session_state.session_id[:8] + "...")

    # Export options
    st.subheader("Export")
    if st.button("Export Conversation"):
        conversation = "\n\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]
        )
        st.download_button(
            "Download Conversation",
            conversation,
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
        )


# Main chat interface
st.title("🤖 AgentAru - Your Personal AI Assistant")
st.caption(
    "Powered by LangGraph with multi-agent orchestration and long-term memory"
)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show metadata if available
        if "metadata" in message:
            with st.expander("Details"):
                st.json(message["metadata"])


# Chat input
if prompt := st.chat_input("What can I help you with?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = agent.run(
                    user_input=prompt, session_id=st.session_state.session_id
                )

                # Extract response
                last_message = result["messages"][-1]
                response = last_message.content

                st.markdown(response)

                # Show agent routing info
                metadata = {
                    "agents_used": result.get("agent_history", []),
                    "task": result.get("current_task", ""),
                    "memories_used": len(result.get("relevant_memories", [])),
                }

                with st.expander("Agent Details"):
                    st.json(metadata)

                # Add assistant message
                st.session_state.messages.append(
                    {"role": "assistant", "content": response, "metadata": metadata}
                )

            except Exception as e:
                st.error(f"Error: {e}")


# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(
    ["💬 Chat", "📧 Email", "📅 Calendar", "💡 Ideas"]
)

with tab1:
    st.info("👆 Use the chat interface above to interact with AgentAru")

with tab2:
    st.subheader("Email Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Read Recent Emails"):
            with st.spinner("Fetching emails..."):
                result = agent.run(
                    user_input="Read my recent emails",
                    session_id=st.session_state.session_id,
                )
                st.write(result["messages"][-1].content)

    with col2:
        if st.button("Check Important"):
            with st.spinner("Checking important emails..."):
                result = agent.run(
                    user_input="Show me important emails",
                    session_id=st.session_state.session_id,
                )
                st.write(result["messages"][-1].content)

with tab3:
    st.subheader("Calendar View")

    if st.button("Show Today's Schedule"):
        with st.spinner("Fetching calendar..."):
            result = agent.run(
                user_input="What's on my calendar today?",
                session_id=st.session_state.session_id,
            )
            st.write(result["messages"][-1].content)

with tab4:
    st.subheader("Ideas & Notes")

    idea_input = st.text_area("Capture a new idea:")
    if st.button("Save Idea"):
        if idea_input:
            with st.spinner("Saving idea..."):
                result = agent.run(
                    user_input=f"Save this idea: {idea_input}",
                    session_id=st.session_state.session_id,
                )
                st.success("Idea saved!")
                st.write(result["messages"][-1].content)


# Footer
st.markdown("---")
st.caption(
    "AgentAru v0.1.0 | Built with LangGraph, LangChain, and Streamlit | "
    f"Model: {settings.default_model}"
)
