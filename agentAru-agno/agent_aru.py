from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

# Create a basic agent with OpenAI gpt-4.1-mini
agent = Agent(
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
    markdown=True
)

# Test the agent with a simple query
if __name__ == "__main__":
    agent.print_response("Hello, I am a user. What can you do as AgentAru?", stream=True) 