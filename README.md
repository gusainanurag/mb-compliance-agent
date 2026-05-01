# MB USA Labour Rate Compliance Agent

An AI agent built with AWS Strands and Amazon Bedrock that automates labour rate compliance checking for Mercedes Benz USA vendor requests.

## Problem
Vendors request labour rate changes which require manual review against legal regulations across 50 US states — a time consuming process for compliance officers.

## Solution
An agentic AI system that:
- Takes vendor, current rate, new rate, and state as input
- Automatically retrieves state-specific labour regulations
- Calculates the rate increase percentage
- Returns a clear COMPLIANT / NON-COMPLIANT decision with reasoning

## Tech Stack
- **AWS Strands** — agent orchestration framework
- **Amazon Bedrock** — LLM inference
- **FastAPI** — REST API layer
- **AWS Lambda** — serverless deployment
- **AWS API Gateway** — public endpoint

## API Usage
**Endpoint:** `POST /check-compliance`

**Request:**
```json
{
  "vendor_name": "ABC Auto Parts",
  "current_rate": 12.0,
  "new_rate": 20.0,
  "state": "california"
}
```

**Response:**
```json
{
  "vendor": "ABC Auto Parts",
  "state": "california",
  "current_rate": 12.0,
  "new_rate": 20.0,
  "compliance_result": "NON-COMPLIANT - 66.7% increase exceeds California's maximum allowed increase of 15%"
}
```

## Architecture
User → API Gateway → Lambda → Strands Agent → Bedrock (Nova Pro) → Tools → Response