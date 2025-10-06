from agents import Agent
from utils import get_emails, get_phone_logs, get_order, retrieve_payment_intent, close_dispute

# Define the Agents
investigator_agent = Agent(
    name="Dispute Intake Agent",
    instructions=(
        "As a dispute investigator, please compile the following details in your final output:\n\n"
        "Dispute Details:\n"
        "- Dispute ID\n"
        "- Amount\n"
        "- Reason for Dispute\n"
        "- Card Brand\n\n"
        "Payment & Order Details:\n"
        "- Fulfillment status of the order\n"
        "- Shipping carrier and tracking number\n"
        "- Confirmation of TOS acceptance\n\n"
        "Email and Phone Records:\n"
        "- Any relevant email threads (include the full body text)\n"
        "- Any relevant phone logs\n"
    ),
    model="o3-mini",
    tools=[get_emails, get_phone_logs]
)

accept_dispute_agent = Agent(
    name="Accept Dispute Agent",
    instructions=(
        "You are an agent responsible for accepting disputes. Please do the following:\n"
        "1. Use the provided dispute ID to close the dispute.\n"
        "2. Provide a short explanation of why the dispute is being accepted.\n"
        "3. Reference any relevant order details (e.g., unfulfilled order, etc.) retrieved from the database.\n\n"
        "Then, produce your final output in this exact format:\n\n"
        "Dispute Details:\n"
        "- Dispute ID\n"
        "- Amount\n"
        "- Reason for Dispute\n\n"
        "Order Details:\n"
        "- Fulfillment status of the order\n\n"
        "Reasoning for closing the dispute\n"
    ),
    model="gpt-4o",
    tools=[close_dispute]
)

triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "Please do the following:\n"
        "1. Find the order ID from the payment intent's metadata.\n"
        "2. Retrieve detailed information about the order (e.g., shipping status).\n"
        "3. If the order has shipped, escalate this dispute to the investigator agent.\n"
        "4. If the order has not shipped, accept the dispute.\n"
    ),
    model="gpt-4o",
    tools=[retrieve_payment_intent, get_order],
    handoffs=[accept_dispute_agent, investigator_agent],
) 