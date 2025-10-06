# AgentAru

A smart agent built using the AGNO framework.

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your_api_key_here  # On Windows: set OPENAI_API_KEY=your_api_key_here
```

4. (Optional) Authenticate with Agno:

```bash
ag setup
```

Or export your AGNO_API_KEY:

```bash
export AGNO_API_KEY=ag-***
```

## Running the Agent

Run the basic agent directly:

```bash
python agent_aru.py
```

## Running the Playground UI

1. Make sure your environment is set up and the OPENAI_API_KEY is exported.

2. Run the playground:

```bash
python playground.py
```

3. Access the playground in one of two ways:
   - Open the link provided in the terminal
   - Navigate to http://app.agno.com/playground (login required) and select the `localhost:7777` endpoint

## Future Enhancements

- Add memory support for persistent conversations
- Integrate more tools for enhanced capabilities
- Add knowledge base for domain-specific information
- Configure storage for session history 