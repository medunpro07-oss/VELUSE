import os
import time
import base64
from datetime import datetime
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive.readonly'
]

def authenticate_workspace():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(host='127.0.0.1', port=8080, open_browser=True)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email(gmail_service, to_email, subject, body_text):
    message = MIMEText(body_text)
    message['to'] = to_email
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        gmail_service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return True
    except Exception as e:
        print(f"[-] Transmission failure to {to_email}: {e}")
        return False

def get_clean_value(row_dict, choices, fallback):
    for choice in choices:
        cleaned_choice = choice.lower().replace("_", " ").strip()
        for k, v in row_dict.items():
            cleaned_k = str(k).lower().replace("_", " ").strip()
            if cleaned_k == cleaned_choice and str(v).strip():
                return str(v).strip()
    return fallback

def execute_sequencer():
    print("[*] Launching Veluse Agency Multi-Stage Outbound Sequencer v3.0...")
    creds = authenticate_workspace()
    gc = gspread.authorize(creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    
    sheet = gc.open('VELUSE // Live Inbound Pipeline Database').worksheet("Outbound_Campaign")
    records = sheet.get_all_records()
    headers = [h.lower().strip().replace(" ", "_") for h in sheet.row_values(1)]
    
    # Track indices for sheet updates
    try:
        t1_status_idx = headers.index('touch_1_status') + 1
        t1_date_idx = headers.index('touch_1_date') + 1
    except ValueError:
        print("[-] Error: Missing sequential tracking headers in the sheet grid.")
        return

    batch_sends = 0
    BATCH_LIMIT = 25
    today_str = datetime.now().strftime("%Y-%m-%d")

    for idx, row in enumerate(records, start=2):
        if batch_sends >= BATCH_LIMIT:
            print("[*] Current iteration batch ceiling reached.")
            break

        # Extract primary email destination
        email = get_clean_value(row, ['emails', 'email'], '').strip()
        if not email or "example.com" in email:
            continue

        # Check multi-stage sequence rules
        t1_status = str(row.get('Touch_1_Status', row.get('touch_1_status', 'PENDING'))).strip().upper()
        
        if t1_status != "PENDING" and t1_status != "":
            continue

        business_name = get_clean_value(row, ['business_name', 'business name', 'clinic_name'], "your practice")
        ai_opener = get_clean_value(row, ['ai_cold_opener', 'ai cold opener'], "noticed you offer high-ticket aesthetic options.")
        pixel_active = str(row.get('Meta Pixel Active', row.get('meta_pixel_active', 'True'))).strip().upper() == 'TRUE'
        tag_active = str(row.get('Google Tag Active', row.get('google_tag_active', 'True'))).strip().upper() == 'TRUE'
        
        # Build dynamic tracking leakage data context
        tracking_leak = "Meta Pixel tracking tags" if not pixel_active else "Google Tag Manager routing configurations"
        if pixel_active and tag_active:
            tracking_leak = "advanced optimization pixels"

        print(f"[*] Dispatching high-intent Touch 1 to: {email}")
        
        subject = f"Question about your {business_name} patient pipeline"
        body = (
            f"Hey,\n\n"
            f"I was looking over your digital layout for {business_name} and wanted to reach out.\n\n"
            f"{ai_opener}\n\n"
            f"We ran a brief diagnostic scan across your landing pages and noticed that your {tracking_leak} is currently down "
            f"or misconfigured. This means you are driving premium patient intent locally but letting them exit without a basic retargeting sequence.\n\n"
            f"We put together a clean 3-point competitor market map showing exactly how to patch this layout and secure those lost bookings. "
            f"Let me know if you want me to drop the 60-second video overview context across to your team. No strings attached.\n\n"
            f"Best,\n"
            f"Medun\n"
            f"Founder, Veluse Agency"
        )

        if send_email(gmail_service, email, subject, body):
            sheet.update_cell(idx, t1_status_idx, "SENT")
            sheet.update_cell(idx, t1_date_idx, today_str)
            batch_sends += 1
            time.sleep(3)  # Inundation safety buffer

    print(f"[*] Complete. Total high-intent touchpoints executed in this run: {batch_sends}")

if __name__ == "__main__":
    execute_sequencer()
