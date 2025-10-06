import os
import json
import logging
import stripe
from dotenv import load_dotenv
from agents import Runner
from agents import triage_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

async def process_dispute(payment_intent_id, triage_agent):
    """Retrieve and process dispute data for a given PaymentIntent."""
    disputes_list = stripe.Dispute.list(payment_intent=payment_intent_id)
    if not disputes_list.data:
        logger.warning("No dispute data found for PaymentIntent: %s", payment_intent_id)
        return None
    
    dispute_data = disputes_list.data[0]
    
    relevant_data = {
        "dispute_id": dispute_data.get("id"),
        "amount": dispute_data.get("amount"),
        "due_by": dispute_data.get("evidence_details", {}).get("due_by"),
        "payment_intent": dispute_data.get("payment_intent"),
        "reason": dispute_data.get("reason"),
        "status": dispute_data.get("status"),
        "card_brand": dispute_data.get("payment_method_details", {}).get("card", {}).get("brand")
    }
    
    event_str = json.dumps(relevant_data)
    # Pass the dispute data to the triage agent
    result = await Runner.run(triage_agent, input=event_str)
    logger.info("WORKFLOW RESULT: %s", result.final_output)
    
    return relevant_data, result.final_output

# Example usage for scenario 1: Company mistake (product not received)
async def scenario_company_mistake():
    payment = stripe.PaymentIntent.create(
        amount=2000,
        currency="usd",
        payment_method="pm_card_createDisputeProductNotReceived",
        confirm=True,
        metadata={"order_id": "1234"},
        off_session=True,
        automatic_payment_methods={"enabled": True},
    )
    relevant_data, triage_result = await process_dispute(payment.id, triage_agent)
    return relevant_data, triage_result

# Example usage for scenario 2: Customer dispute (final sale)
async def scenario_customer_dispute():
    payment = stripe.PaymentIntent.create(
        amount=2000,
        currency="usd",
        payment_method="pm_card_createDispute",
        confirm=True,
        metadata={"order_id": "1121"},
        off_session=True,
        automatic_payment_methods={"enabled": True},
    )
    relevant_data, triage_result = await process_dispute(payment.id, triage_agent)
    return relevant_data, triage_result

# Main function to run scenarios
async def main():
    print("Running Scenario 1: Company Mistake (Product Not Received)")
    data1, result1 = await scenario_company_mistake()
    print(f"Dispute Data: {json.dumps(data1, indent=2)}")
    print(f"Result: {result1}")
    
    print("\nRunning Scenario 2: Customer Dispute (Final Sale)")
    data2, result2 = await scenario_customer_dispute()
    print(f"Dispute Data: {json.dumps(data2, indent=2)}")
    print(f"Result: {result2}")

# Run the main function asynchronously
if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 