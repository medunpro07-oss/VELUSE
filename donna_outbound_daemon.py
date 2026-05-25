import os
import time
import base64
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
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_html_email(gmail_service, to_email, subject, body_text):
    message = MIMEText(body_text)
    message['to'] = to_email
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        gmail_service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return True
    except Exception as e:
        print(f"[-] Gmail API transmission failure: {e}")
        return False

def get_clean_value(row_dict, choices, fallback):
    """Searches row record case-insensitively for variations of requested headers."""
    for choice in choices:
        cleaned_choice = choice.lower().replace("_", " ").strip()
        for k, v in row_dict.items():
            cleaned_k = str(k).lower().replace("_", " ").strip()
            if cleaned_k == cleaned_choice and str(v).strip():
                return str(v).strip()
    return fallback

def execute_autonomous_outbound():
    print("[*] Activating Donna Workspace Outbound Matrix v2.0...")
    creds = authenticate_workspace()
    
    gc = gspread.authorize(creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    
    try:
        sheet = gc.open('VELUSE // Live Inbound Pipeline Database').worksheet("Outbound_Campaign")
    except Exception as e:
        print(f"[-] Configuration Error: Could not access sheet/worksheet. Error: {e}")
        return

    records = sheet.get_all_records()
    headers = sheet.row_values(1)
    
    # Isolate Status column index for precise sheet mutations
    try:
        status_idx = next(i for i, h in enumerate(headers, start=1) if h.lower().strip() == 'status')
    except StopIteration:
        print("[-] Critical Error: 'Status' column not found in sheet headers.")
        return

    send_count = 0
    max_daily_sends = 25
    
    for idx, row in enumerate(records, start=2):
        if send_count >= max_daily_sends:
            print("[*] Daily safety volume ceiling reached. Throttling queue.")
            break
            
        status = str(row.get('Status', row.get('status', ''))).strip().upper()
        if status != "PENDING":
            continue
            
        email = str(row.get('Email', row.get('email', ''))).strip()
        if not email:
            continue
            
        variant = str(row.get('Variant', row.get('variant', 'A'))).strip().upper()
        
        # Dynamic Flexible Field Resolution with Optimized Fallbacks
        raw_owner = get_clean_value(row, ['owner_name', 'owner name', 'first_name', 'name'], '')
        greeting = f"Hey {raw_owner}," if raw_owner else "Hey,"
        
        business_name = get_clean_value(row, ['clinic_name', 'clinic name', 'business_name', 'business name', 'name'], "your practice")
        top_service = get_clean_value(row, ['top_service', 'top service', 'service'], "Morpheus8")
        city = get_clean_value(row, ['city', 'location'], "local")
        latest_offer = get_clean_value(row, ['latest_offer', 'latest offer', 'offer'], "active promotion")
        tracking_leak = get_clean_value(row, ['tracking_leak', 'tracking leak', 'leak'], "Meta Pixel tracking")
        
        print(f"[*] Compiling Variant {variant} specialized payload for: {email}")
        
        if variant == "A":
            subject = f"Quick question about your {top_service} capacity"
            body = (
                f"{greeting}\n\n"
                f"I noticed you’re running the {top_service} platform over at {business_name}.\n\n"
                f"Quick logistical question—are your treatment rooms for {top_service} currently maxed out this month, "
                f"or do you have open blocks you're trying to pack out in the {city} market?\n\n"
                f"We just mapped the local search metrics for your zip code and noticed your direct competitor is capturing "
                f"roughly 70% of the active high-ticket patient traffic. I put together a quick, 60-second competitor market gap "
                f"blueprint showing exactly how to redirect those open cycles into your vacant slots.\n\n"
                f"Happy to drop the link over for free if you want to take a look. If you’re already overbooked, just ignore this.\n\n"
                f"Best,\n"
                f"Medun\n"
                f"Founder, Veluse Agency"
            )
        else:
            subject = f"Drop-off on your {latest_offer} page?"
            body = (
                f"{greeting}\n\n"
                f"I was looking over your {latest_offer} package on your website.\n\n"
                f"I ran a quick diagnostic scan on your landing page and noticed that your {tracking_leak} is currently down "
                f"or completely uninstalled. This means you are paying to attract local patient intent but letting them leave "
                f"without setting up a basic retargeting sequence.\n\n"
                f"We mapped out a quick 3-point technical fix to plug this leak and secure the traffic you're already generating.\n\n"
                f"Let me know if you want me to drop over the 60-second walkthrough video. No strings attached—you can pass it "
                f"straight to your web dev team to patch it.\n\n"
                f"Best,\n"
                f"Medun\n"
                f"Founder, Veluse Agency"
            )
            
        success = send_html_email(gmail_service, email, subject, body)
        
        if success:
            sheet.update_cell(idx, status_idx, f"SENT: VARIANT {variant}")
            print(f"[+] Operational hit successful. Row {idx} updated.")
            send_count += 1
            time.sleep(3)
        else:
            sheet.update_cell(idx, status_idx, "ERROR: TRANSMISSION_FAILED")

    print(f"[*] Batch completion report. Total successful deliveries: {send_count}")

if __name__ == "__main__":
    execute_autonomous_outbound()
