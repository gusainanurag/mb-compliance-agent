from fastapi import FastAPI
from pydantic import BaseModel
from mangum import Mangum
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

app = FastAPI(title="MB USA Labour Rate Compliance Checker", root_path="/prod")

# Request model
class ComplianceRequest(BaseModel):
    vendor_name: str
    current_rate: float
    new_rate: float
    state: str

# Tools
@tool
def check_state_regulations(state: str, labour_rate_increase: float) -> str:
    """
    Check labour rate regulations for a specific US state.
    
    Args:
        state (str): The US state to check regulations for
        labour_rate_increase (float): The requested hourly rate increase in USD
    
    Returns:
        str: Relevant regulation information for the state
    """
    regulations = {
        "california": {
            "min_wage": 16.00,
            "max_increase_percent": 15,
            "notice_period_days": 30,
            "notes": "California requires 30 days notice for rate changes above 10%"
        },
        "texas": {
            "min_wage": 7.25,
            "max_increase_percent": 25,
            "notice_period_days": 14,
            "notes": "Texas follows federal guidelines with minimal state restrictions"
        },
        "new york": {
            "min_wage": 16.00,
            "max_increase_percent": 12,
            "notice_period_days": 45,
            "notes": "New York requires written approval for increases above 10%"
        }
    }
    
    state_lower = state.lower()
    if state_lower in regulations:
        reg = regulations[state_lower]
        return f"""
        State: {state}
        Minimum Wage: ${reg['min_wage']}/hour
        Maximum Allowed Increase: {reg['max_increase_percent']}%
        Required Notice Period: {reg['notice_period_days']} days
        Additional Notes: {reg['notes']}
        Requested Increase: ${labour_rate_increase}/hour
        """
    else:
        return f"Regulations for {state} not found in database. Manual review required."

@tool
def calculate_increase_percentage(current_rate: float, new_rate: float) -> str:
    """
    Calculate the percentage increase between current and new labour rates.
    
    Args:
        current_rate (float): Current hourly rate in USD
        new_rate (float): Proposed new hourly rate in USD
    
    Returns:
        str: Percentage increase and analysis
    """
    increase = new_rate - current_rate
    percentage = (increase / current_rate) * 100
    return f"Rate increase: ${increase:.2f}/hour ({percentage:.1f}% increase)"

# Initialize model
model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

# Initialize agent
agent = Agent(
    model=model,
    tools=[check_state_regulations, calculate_increase_percentage],
    system_prompt="""You are a labour rate compliance checker for Mercedes Benz USA. 
    Your job is to evaluate vendor labour rate increase requests against state regulations.
    Always check the state regulations and calculate the increase percentage before giving a compliance decision.
    Be clear about whether the request is COMPLIANT or NON-COMPLIANT and explain why."""
)

@app.post("/check-compliance")
async def check_compliance(request: ComplianceRequest):
    query = f"""
    Vendor: {request.vendor_name}
    Current Rate: ${request.current_rate}/hour
    Requested New Rate: ${request.new_rate}/hour
    State: {request.state}
    
    Please check if this labour rate increase is compliant with state regulations.
    """
    
    response = agent(query)
    return {
        "vendor": request.vendor_name,
        "state": request.state,
        "current_rate": request.current_rate,
        "new_rate": request.new_rate,
        "compliance_result": str(response)
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Lambda handler
handler = Mangum(app)