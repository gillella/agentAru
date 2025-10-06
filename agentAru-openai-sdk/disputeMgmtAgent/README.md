# Dispute Management Agent

This project demonstrates how to use OpenAI's Agents SDK and Stripe API to automate dispute management workflows. It implements a system of specialized agents that work together to handle payment disputes efficiently.

## Agents Overview

1. **Triage Agent**: Determines whether to accept or escalate a dispute based on the order's fulfillment status
2. **Acceptance Agent**: Automatically accepts disputes for unfulfilled orders
3. **Investigator Agent**: Gathers evidence for disputes that need further investigation

## Setup Instructions

### Prerequisites

1. OpenAI API Key
2. Stripe API Key (Test mode)

### Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   STRIPE_SECRET_KEY=your_stripe_secret_key_here
   ```

## Usage

Run the main script to see the agents in action handling two sample dispute scenarios:

```
python main.py
```

### Scenario 1: Company Mistake
Demonstrates a case where an order wasn't shipped and the dispute should be accepted.

### Scenario 2: Customer Dispute (Final Sale)
Demonstrates a case where an order was delivered, but the customer is disputing it despite the final sale terms.

## Project Structure

- `main.py`: Entry point with example dispute scenarios
- `agents.py`: Definition of the three dispute management agents
- `utils.py`: Helper functions and tools used by the agents

## Further Customization

You can extend this project by:
- Adding more sophisticated dispute scenarios
- Implementing additional agent types for specific dispute reasons
- Connecting to your actual order database instead of using mock data 