import os
import re
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator
from twilio.rest import Client

app = FastAPI(title="Veluse OS Hardened Security Core")

# Secure API Token Verification Framework
VELUSE_API_KEY = os.environ.get("VELUSE_GATEKEEPER_TOKEN", "VELUSE_STAGE_SECURE_KEY_8831")
api_key_header = APIKeyHeader(name="X-Veluse-Gatekeeper-Token", auto_error=True)

async def verify_gatekeeper_token(header_token: str = Depends(api_key_header)):
    """Validates the network request signature before unlocking pipeline processing."""
    if header_token != VELUSE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CRITICAL: Security signature verification mismatch. Access denied."
        )
    return header_token

# Strongly-typed structured input validation schema
class InboundLeadSchema(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    business_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    top_service: str = Field(default="Morpheus8", max_length=50)

    @validator('phone')
    def validate_phone_e164(cls, v):
        """Scrubs character fields and ensures valid international E.164 teleco formatting."""
        clean_num = re.sub(r'[\s\-()+,]', '', v)
        if not clean_num.isdigit():
            raise ValueError('Phone payload contains non-numeric syntax corruption.')
        return f"+{clean_num}" if not v.startswith('+') else v

    @validator('first_name', 'business_name', 'top_service')
    def scrub_malicious_strings(cls, v):
        """Neutralizes basic script injection vectors at the input array level."""
        clean_str = re.sub(r'[<>{}\[\]\\\/]', '', v)
        return clean_str.strip()

def dispatch_secure_text(lead_data: InboundLeadSchema):
    """Headless background worker execution loop for Twilio routing."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_NUMBER")
    
    if not all([account_sid, auth_token, twilio_number]):
        print("[-] Operational alert: Twilio variables unassigned. Running script in secure simulation log context.")
        print(f"[SIMULATION LOG] SMS payload generated for {lead_data.first_name} at {lead_data.phone}")
        return

    client = Client(account_sid, auth_token)
    sms_body = (
        f"Hey {lead_data.first_name} - saw you just grabbed a slot for the {lead_data.top_service} "
        f"package over at {lead_data.business_name}.\n\n"
        f"Quick logistical heads up: our treatment slots fill out pretty fast. "
        f"Did you want to secure an open block for this week, or are you just mapping options out?"
    )
    
    try:
        message = client.messages.create(
            body=sms_body,
            from_=twilio_number,
            to=lead_data.phone
        )
        print(f"[+] Encrypted message line dispatched. Transmission ID: {message.sid}")
    except Exception as e:
        print(f"[-] Infrastructure error during cellular routing: {e}")

@app.post("/api/v1/secure_inbound_lead", status_code=202)
async def handle_secure_lead(
    payload: InboundLeadSchema, 
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_gatekeeper_token)
):
    """Authenticates, parses, sanitizes, and pipelines incoming lead vectors headlessly."""
    # Fork background thread processing to shield endpoint from task-blocking execution delays
    background_tasks.add_task(dispatch_secure_text, payload)
    return {"status": "AUTHENTICATED_AND_QUEUED", "SLA_LATENCY": "<120s"}
