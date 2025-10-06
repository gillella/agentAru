# AgentAru Architecture Diagram

## Complete System Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                                 │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │
│  │  Streamlit UI   │  │   CLI (REPL)    │  │  MCP-Enhanced CLI   │  │
│  │   (Web App)     │  │  (main.py)      │  │   (main_mcp.py) 🔥  │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────┬───────────┘  │
└───────────┼───────────────────┼──────────────────────┼────────────────┘
            │                   │                       │
            └───────────────────┴───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   AgentAru Core App     │
                    │  (Initialization &      │
                    │   Orchestration)        │
                    └────────────┬────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Model Manager   │  │ Memory Manager  │  │  MCP Manager 🔥 │
│                 │  │                 │  │                 │
│ • Claude        │  │ • Mem0          │  │ • MCP Client    │
│ • GPT-4         │  │ • ChromaDB      │  │ • Tool Manager  │
│ • Ollama        │  │ • Decay         │  │ • Config Mgr    │
│ • Caching       │  │ • 3 Types       │  │ • Servers       │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                ┌─────────────▼─────────────┐
                │   LangGraph Orchestrator  │
                │   (State Machine)         │
                │                           │
                │  ┌─────────────────────┐  │
                │  │  Supervisor Node    │  │
                │  │  (Routing Logic)    │  │
                │  └──────────┬──────────┘  │
                │             │             │
                │   ┌─────────┴──────────┐  │
                │   │                    │  │
                │   ▼         ▼          ▼  │
                │  ┌──┐      ┌──┐      ┌──┐│
                │  │📧│      │📅│      │💡││
                │  └──┘      └──┘      └──┘│
                │   │         │          │  │
                │   ▼         ▼          ▼  │
                │  Email   Calendar    Idea │
                │  Agent    Agent     Agent │
                │                           │
                │            ▼              │
                │        ┌───────┐          │
                │        │🔧 MCP │ 🔥       │
                │        │ Agent │          │
                │        └───┬───┘          │
                │            │              │
                │  ┌─────────▼─────────┐    │
                │  │  Memory Update    │    │
                │  │      Node         │    │
                │  └───────────────────┘    │
                └───────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Integrations   │  │  MCP Servers 🔥 │  │    Memory       │
│                 │  │                 │  │    Storage      │
│ • Gmail API     │  │ • Filesystem    │  │                 │
│ • Google Cal    │  │ • Web Search    │  │ • Vector DB     │
│ • OAuth2        │  │ • GitHub        │  │ • Mem0 Cloud    │
│                 │  │ • SQLite        │  │ • Local Cache   │
│                 │  │ • Slack         │  │                 │
│                 │  │ • Google Drive  │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Data Flow

### 1. Request Processing Flow
```
User Input
   │
   ▼
[Parse & Initialize State]
   │
   ▼
[Retrieve Relevant Memories]
   │
   ▼
Supervisor Agent (Routing Decision)
   │
   ├─→ Email Agent ──┐
   ├─→ Calendar Agent─┤
   ├─→ Idea Agent ────┤
   └─→ MCP Agent 🔥 ──┘
        │
        ▼
   [Execute Task]
        │
        ▼
   [Update Memory]
        │
        ▼
   [Return Response]
        │
        ▼
     User
```

### 2. MCP Tool Execution Flow 🔥
```
MCP Agent Request
       │
       ▼
  MCP Manager
       │
       ├─→ [Check Connected Servers]
       │
       ▼
  Select Server
       │
       ├─→ Filesystem Server
       ├─→ Web Search Server
       ├─→ GitHub Server
       └─→ Custom Servers
            │
            ▼
       [Call Tool]
            │
            ▼
       [Get Result]
            │
            ▼
    [Return to Agent]
```

### 3. Memory Flow
```
Conversation Interaction
        │
        ▼
   Extract Content
        │
        ├─→ Episodic Memory (conversations)
        ├─→ Semantic Memory (facts)
        └─→ Procedural Memory (how-to)
             │
             ▼
        Store in Mem0
             │
             ▼
        Vector Embedding
             │
             ▼
        ChromaDB Storage
             │
             ▼
   [Decay Applied Over Time]
             │
             ▼
   [Retrieved When Relevant]
```

## Component Interactions

### Model Manager Flow
```
Agent Request
     │
     ▼
Model Manager
     │
     ├─→ [Check Cache]
     │   │
     │   ├─→ Found → Return Cached Model
     │   └─→ Not Found ↓
     │
     ├─→ [Detect Provider]
     │   ├─→ Anthropic
     │   ├─→ OpenAI
     │   └─→ Ollama
     │
     ├─→ [Validate API Key]
     │
     ├─→ [Create Model Instance]
     │
     ├─→ [Cache for Reuse]
     │
     └─→ [Return to Agent]
```

### MCP Integration Flow 🔥
```
Application Start
       │
       ▼
  MCP Manager Init
       │
       ├─→ Load Config (mcp_servers.yaml)
       │
       ├─→ Auto-connect Servers (if enabled)
       │   │
       │   ├─→ Start Server Process
       │   ├─→ Establish stdio Connection
       │   ├─→ Initialize Session
       │   └─→ List Tools
       │
       ├─→ Register Tools with Tool Manager
       │   │
       │   ├─→ Create LangChain Wrappers
       │   ├─→ Add to Registry
       │   └─→ Make Available to Agents
       │
       └─→ Ready for Use
```

## Agent State Machine

```
[ENTRY]
   │
   ▼
┌─────────────┐
│ SUPERVISOR  │
│   (Route)   │
└──────┬──────┘
       │
       │ ┌────────────────────────┐
       ├→│ Email Agent            │→┐
       │ └────────────────────────┘ │
       │                            │
       │ ┌────────────────────────┐ │
       ├→│ Calendar Agent         │→┤
       │ └────────────────────────┘ │
       │                            │
       │ ┌────────────────────────┐ │
       ├→│ Idea Agent             │→┤
       │ └────────────────────────┘ │
       │                            │
       │ ┌────────────────────────┐ │
       ├→│ MCP Agent 🔥           │→┤
       │ └────────────────────────┘ │
       │                            │
       └→ [Task Complete?] ←────────┘
              │        │
              No       Yes
              │        │
              ↑        ▼
          [Loop]  ┌─────────────┐
                  │Memory Update│
                  └──────┬──────┘
                         │
                         ▼
                      [END]
```

## Technology Stack Layers

```
┌─────────────────────────────────────────────┐
│          Application Layer                   │
│  • Streamlit UI                             │
│  • CLI Interface                            │
│  • MCP-Enhanced CLI 🔥                      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Orchestration Layer                │
│  • LangGraph (State Machine)                │
│  • Agent Routing                            │
│  • State Management                         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Agent Layer                        │
│  • Supervisor Agent                         │
│  • Specialized Agents (Email, Cal, Idea)    │
│  • MCP Agent 🔥                             │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Service Layer                      │
│  • Model Manager (Multi-LLM)                │
│  • Memory Manager (Mem0)                    │
│  • MCP Manager 🔥 (Protocol Client)         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Integration Layer                  │
│  • LangChain (LLM Abstraction)              │
│  • MCP Protocol 🔥 (Tool Standard)          │
│  • Google APIs (Gmail, Calendar)            │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Storage Layer                      │
│  • ChromaDB (Vector Store)                  │
│  • Mem0 (Semantic Memory)                   │
│  • Local File System                        │
│  • MCP Servers 🔥 (External Tools)          │
└─────────────────────────────────────────────┘
```

## Key Features Visualization

### Multi-Model Support
```
User Query
    │
    ▼
┌─────────────────────┐
│   Model Manager     │
│                     │
│  Available Models:  │
│  ┌───────────────┐  │
│  │ Claude 3.5    │  │
│  │ Sonnet        │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Claude 3.5    │  │
│  │ Haiku         │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ GPT-4o        │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Llama 3.1     │  │
│  └───────────────┘  │
└─────────────────────┘
         │
         ▼
    Selected Model
```

### MCP Server Ecosystem 🔥
```
       ┌─────────────────┐
       │   MCP Manager   │
       └────────┬────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
    ▼           ▼           ▼
┌────────┐  ┌────────┐  ┌────────┐
│Filesys │  │  Web   │  │ GitHub │
│ tem    │  │ Search │  │        │
└────────┘  └────────┘  └────────┘
    ▼           ▼           ▼
┌────────┐  ┌────────┐  ┌────────┐
│ SQLite │  │ Slack  │  │ Google │
│        │  │        │  │ Drive  │
└────────┘  └────────┘  └────────┘
     │           │          │
     └───────────┴──────────┘
                 │
                 ▼
          Unified Tool API
```

### Memory System
```
    Conversation
         │
         ▼
    ┌─────────────┐
    │  Extract    │
    │  Content    │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐   ┌────────┐
│ Mem0   │   │ Vector │
│Semantic│   │Embedding│
└───┬────┘   └────┬───┘
    │             │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  ChromaDB   │
    │   Storage   │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   Decay     │
    │  Algorithm  │
    └──────┬──────┘
           │
           ▼
    Relevant Context
```

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│           Production Deploy             │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │        Load Balancer             │  │
│  └───────────────┬──────────────────┘  │
│                  │                     │
│     ┌────────────┴────────────┐        │
│     │                         │        │
│     ▼                         ▼        │
│  ┌──────┐                 ┌──────┐     │
│  │ App  │                 │ App  │     │
│  │ Inst │                 │ Inst │     │
│  │ 1    │                 │ 2    │     │
│  └──┬───┘                 └───┬──┘     │
│     │                         │        │
│     └─────────┬───────────────┘        │
│               │                        │
│               ▼                        │
│  ┌─────────────────────────────────┐   │
│  │      Shared Services            │   │
│  │                                 │   │
│  │  • Redis (Caching)              │   │
│  │  • PostgreSQL (Metadata)        │   │
│  │  • ChromaDB (Vectors)           │   │
│  │  • Mem0 Cloud (Memory)          │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

**Legend:**
- 🔥 = New MCP features
- 📧 = Email
- 📅 = Calendar
- 💡 = Ideas
- 🔧 = MCP Tools

---

This diagram represents the complete AgentAru architecture with full MCP integration!
