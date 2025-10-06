import os
import logging
import json
import stripe
from agents import function_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Stripe API key from environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@function_tool
def get_phone_logs(phone_number: str) -> list:
    """
    Return a list of phone call records for the given phone number.
    Each record might include call timestamps, durations, notes, 
    and an associated order_id if applicable.
    """
    phone_logs = [
        {
            "phone_number": "+15551234567",
            "timestamp": "2023-03-14 15:24:00",
            "duration_minutes": 5,
            "notes": "Asked about status of order #1121",
            "order_id": 1121
        },
        {
            "phone_number": "+15551234567",
            "timestamp": "2023-02-28 10:10:00",
            "duration_minutes": 7,
            "notes": "Requested refund for order #1121, I told him we were unable to refund the order because it was final sale",
            "order_id": 1121
        },
        {
            "phone_number": "+15559876543",
            "timestamp": "2023-01-05 09:00:00",
            "duration_minutes": 2,
            "notes": "General inquiry; no specific order mentioned",
            "order_id": None
        },
    ]
    return [
        log for log in phone_logs if log["phone_number"] == phone_number
    ]


@function_tool
def get_order(order_id: int) -> str:
    """
    Retrieve an order by ID from a predefined list of orders.
    Returns the corresponding order object or 'No order found'.
    """
    orders = [
        {
            "order_id": 1234,
            "fulfillment_details": "not_shipped"
        },
        {
            "order_id": 9101,
            "fulfillment_details": "shipped",
            "tracking_info": {
                "carrier": "FedEx",
                "tracking_number": "123456789012"
            },
            "delivery_status": "out for delivery"
        },
        {
            "order_id": 1121,
            "fulfillment_details": "delivered",
            "customer_id": "cus_PZ1234567890",
            "customer_phone": "+15551234567",
            "order_date": "2023-01-01",
            "customer_email": "customer1@example.com",
            "tracking_info": {
                "carrier": "UPS",
                "tracking_number": "1Z999AA10123456784",
                "delivery_status": "delivered"
            },
            "shipping_address": {
                "zip": "10001"
            },
            "tos_acceptance": {
                "date": "2023-01-01",
                "ip": "192.168.1.1"
            }
        }
    ]
    for order in orders:
        if order["order_id"] == order_id:
            return order
    return "No order found"


@function_tool
def get_emails(email: str) -> list:
    """
    Return a list of email records for the given email address.
    """
    emails = [
        {
            "email": "customer1@example.com",
            "subject": "Order #1121",
            "body": "Hey, I know you don't accept refunds but the sneakers don't fit and I'd like a refund"
        },
        {
            "email": "customer2@example.com",
            "subject": "Inquiry about product availability",
            "body": "Hello, I wanted to check if the new model of the smartphone is available in stock."
        },
        {
            "email": "customer3@example.com",
            "subject": "Feedback on recent purchase",
            "body": "Hi, I recently purchased a laptop from your store and I am very satisfied with the product. Keep up the good work!"
        }
    ]
    return [email_data for email_data in emails if email_data["email"] == email]


@function_tool
async def retrieve_payment_intent(payment_intent_id: str) -> dict:
    """
    Retrieve a Stripe payment intent by ID.
    Returns the payment intent object on success or an empty dictionary on failure.
    """
    try:
        return stripe.PaymentIntent.retrieve(payment_intent_id)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error occurred while retrieving payment intent: {e}")
        return {}

@function_tool
async def close_dispute(dispute_id: str) -> dict:
    """
    Close a Stripe dispute by ID. 
    Returns the dispute object on success or an empty dictionary on failure.
    """
    try:
        return stripe.Dispute.close(dispute_id)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error occurred while closing dispute: {e}")
        return {} 