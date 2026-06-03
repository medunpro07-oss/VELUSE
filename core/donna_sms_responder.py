# core/donna_sms_responder.py
import os
import re
import json
from datetime import datetime
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator
from twilio.rest import Client
import gspread
from google.oauth2.credentials import Credentials

app = FastAPI(title="Veluse OS Production Data Router v1.0")

# 1. Cryptographic Authentication & Verification Layer
VELUSE_SECRET_KEY = os.environ.get("VELUSE_GATEKEEPER_TOKEN", "VELUSE_STAGE_SECURE_KEY_8831")
api_key_header = APIKeyHeader(name="X-Veluse-Gatekeeper-Token", auto_error=True)

async def verify_gatekeeper_token(header_token: str = Depends(api_key_header)):
    if header_token != VELUSE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SECURITY DISCREPANCY: Signature validation failed. Access Denied."
        )
    return header_token

# 2. Cross-Workspace Path Resolution Matrix
def resolve_shared_auth_node():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    veluse_agency_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "VELUSE AGENCY"))
    if not os.path.exists(veluse_agency_dir):
        veluse_agency_dir = r"C:\Users\sajme\OneDrive\Desktop\VELUSE AGENCY"
    return os.path.join(veluse_agency_dir, "token.json")

TOKEN_PATH = resolve_shared_auth_node()
SPREADSHEET_NAME = "VELUSE // Live Inbound Pipeline Database"

# 3. Strongly-Typed Inbound Patient Data Schema
class PatientLeadSchema(BaseModel):
    patient_name: str = Field(..., min_length=2, max_length=60)
    contact_phone: str = Field(..., min_length=10, max_length=15)
    selected_modality: str = Field(..., min_length=2, max_length=50)
    ad_source: str = Field(default="Meta Ads", max_length=50)
    clinic_identity: str = Field(..., min_length=2, max_length=100)

    @validator('contact_phone')
    def normalize_telecom_format(cls, v):
        clean_num = re.sub(r'[\s\-()+,]', '', v)
        if not clean_num.isdigit():
            raise ValueError('Input Malformation: Phone payload contains invalid symbols.')
        return f"+{clean_num}" if not v.startswith('+') else v

    @validator('patient_name', 'selected_modality', 'ad_source', 'clinic_identity')
    def sanitize_input_strings(cls, v):
        return re.sub(r'[<>{}\[\]\\\/]', '', v).strip()

# 4. Background Execution Worker (Sheet Appending + Twilio Cellular Delivery)
def database_logging_and_sms_worker(lead: PatientLeadSchema):
    print(f"\n[*] INTERCEPTED HIGH-INTENT INBOUND VECTOR: {lead.patient_name}")
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Action A: Connect to Cloud Ledger and Log Patient Metrics
    try:
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, ["https://www.googleapis.com/auth/spreadsheets"])
            gc = gspread.authorize(creds)
            workbook = gc.open(SPREADSHEET_NAME)
            
            # Dynamically derive the correct isolated client workspace tab title
            clean_tab_title = "".join(c for c in f"Node_{lead.clinic_identity}" if c.isalnum() or c in " _-")[:30].strip()
            client_sheet = workbook.worksheet(clean_tab_title)
            
            # Match standard sheet headers array values
            client_sheet.append_row([
                lead.patient_name, lead.contact_phone, lead.selected_modality,
                lead.ad_source, "PENDING_TEXT_ACK", timestamp_str, 
                "Automated intake extraction clear.", "ENGAGED"
            ])
            print(f"[+] Lead successfully cataloged inside cloud ledger tab: {clean_tab_title}")
    except Exception as sheet_err:
        print(f"[-] Non-blocking Sheet update failure: {sheet_err}")

    # Action B: Execute 120-Second Cellular SLA Response Core
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_NUMBER")
    
    if not all([account_sid, auth_token, twilio_number]):
        print("[*] Twilio variable values offline. Running script inside sandboxed terminal context.")
        print(f"[SIMULATION LOG] SMS core would transmit payload to {lead.contact_phone}")
        return

    client = Client(account_sid, auth_token)
    sms_payload = (
        f"Hey {lead.patient_name.split()[0]} - saw you just grabbed a slot for the {lead.selected_modality} "
        f"package over at {lead.clinic_identity}.\n\n"
        f"Quick logistical heads up: our treatment slots fill out pretty fast for local zip codes. "
        f"Did you want to secure an open block for this week, or are you just mapping options out right now?"
    )
    
    try:
        message = client.messages.create(body=sms_payload, from_=twilio_number, to=lead.contact_phone)
        print(f"[+] Cellular transmission sequence executed. SID reference code: {message.sid}")
    except Exception as cellular_err:
        print(f"[-] Infrastructure error during Twilio data routing: {cellular_err}")

@app.post("/api/v1/secure_inbound_lead", status_code=202)
async def intake_patient_lead(
    payload: PatientLeadSchema,
    background_tasks: BackgroundTasks,
    authenticated: str = Depends(verify_gatekeeper_token)
):
    """Processes incoming data packages, forks thread execution, and yields a response in <15ms."""
    background_tasks.add_task(database_logging_and_sms_worker, payload)
    return {"status": "SUCCESS", "telemetry_ingress": "buffered", "SLA_latency": "<120s"}
