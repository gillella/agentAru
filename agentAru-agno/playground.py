from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

agent_storage = "data/agentAru.db"

agent_aru = Agent(
    name="AgentAru",
    model=OpenAIChat(id="gpt-4.1-mini"),  # Using gpt-4o-mini as the closest to gpt-4.1-mini
    tools=[
        ReasoningTools(add_instructions=True),
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            company_news=True
        )
    ],
    instructions=[
        "I am AgentAru, a helpful and friendly AI assistant.",
        "When asked about stocks, provide price information, analyst recommendations, and related news.",
        "Summarize stock information in a concise and informative manner.",
        "Always present stock data in tables when appropriate.",
        "Include sources and timestamps for financial information."
    ],
    # Store the agent sessions in a sqlite database
    storage=SqliteStorage(table_name="agent_aru", db_file=agent_storage),
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=5,
    # Adds markdown formatting to the messages
    markdown=True,
)

app = Playground(agents=[agent_aru]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True) 