import os
from fastapi import FastAPI, Request, BackgroundTasks, Response
from twilio.rest import Client

app = FastAPI(title="Veluse OS SMS Core Router")

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")

def dispatch_instant_text(contact_phone: str, first_name: str, clinic_name: str, top_service: str):
    """Executes the 120-second SLA pattern-interrupt text flow."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Conversations must sound conversational, dropped from an iPhone between cycles
    sms_payload = (
        f"Hey {first_name} - saw you just grabbed a slot for the {top_service} "
        f"package over at {clinic_name}.\n\n"
        f"Quick logistical heads up: our treatment slots fill out pretty fast "
        f"for local zip codes. Did you want to secure an open block for this week, "
        f"or are you just mapping options out right now?"
    )
    
    try:
        message = client.messages.create(
            body=sms_payload,
            from_=TWILIO_NUMBER,
            to=contact_phone
        )
        print(f"[+] Instant text dispatched via Donna Core. SID: {message.sid}")
    except Exception as e:
        print(f"[-] SMS delivery failure to node {contact_phone}: {e}")

@app.post("/api/v1/inbound_lead")
async def handle_new_lead_webhook(request: Request, background_tasks: BackgroundTasks):
    """Intercepts leads from landing page forms or GoHighLevel catch-hooks instantly."""
    payload = await request.json()
    
    # Extract structural telemetry fields
    contact_phone = payload.get("phone", "").strip()
    first_name = payload.get("first_name", "there").strip()
    clinic_name = payload.get("business_name", "your practice").strip()
    top_service = payload.get("top_service", "Morpheus8").strip()
    
    if not contact_phone:
        return Response(content='{"status": "MISSING_PHONE_NODE"}', status_code=400)
        
    # Queue the task to clear the main thread instantly and protect execution uptime
    background_tasks.add_task(
        dispatch_instant_text, 
        contact_phone, 
        first_name, 
        clinic_name, 
        top_service
    )
    
    return {"status": "TRANSMISSION_SECURED", "timestamp": "queued"}
