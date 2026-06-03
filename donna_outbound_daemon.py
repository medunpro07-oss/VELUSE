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
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[*] Token refresh failed: {e}. Restarting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(
                    host='127.0.0.1',
                    port=8080,
                    open_browser=True,
                    authorization_prompt_message='[*] Visit the link to authorize the Veluse Agency pipeline: {url}'
                )
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(
                host='127.0.0.1',
                port=8080,
                open_browser=True,
                authorization_prompt_message='[*] Visit the link to authorize the Veluse Agency pipeline: {url}'
            )
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return creds

def send_email(gmail_service, to_email, subject, body_html):
    message = MIMEText(body_html, "html")
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
        
        tracking_token = base64.b64encode(str(idx).encode()).decode().replace("=", "")
        
        subject = f"Question about your {business_name} patient pipeline"
        body_html = (
            f"<html>"
            f"<body>"
            f"<p>Hey,</p>"
            f"<p>I was looking over your digital layout for {business_name} and wanted to reach out.</p>"
            f"<p>{ai_opener}</p>"
            f"<p>We ran a brief diagnostic scan across your landing pages and noticed that your {tracking_leak} is currently down "
            f"or misconfigured. This means you are driving premium patient intent locally but letting them exit without a basic retargeting sequence.</p>"
            f"<p>We put together a clean 3-point competitor market map showing exactly how to patch this layout and secure those lost bookings. "
            f"You can review our profile at <a href=\"https://veluse.vercel.app/?utm_source=outbound&utm_campaign=touch1&utm_term={idx}\">veluse.vercel.app</a>.</p>"
            f"<p>Let me know if you want me to drop the 60-second video overview context across to your team. No strings attached.</p>"
            f"<p>Best,<br />"
            f"Medun<br />"
            f"Founder, Veluse Agency</p>"
            f"<img src=\"https://veluse.vercel.app/api/track?id={tracking_token}\" width=\"1\" height=\"1\" style=\"display:none !important;\" />"
            f"</body>"
            f"</html>"
        )

        if send_email(gmail_service, email, subject, body_html):
            sheet.update_cell(idx, t1_status_idx, "SENT")
            sheet.update_cell(idx, t1_date_idx, today_str)
            batch_sends += 1
            time.sleep(3)  # Inundation safety buffer

    print(f"[*] Complete. Total high-intent touchpoints executed in this run: {batch_sends}")

# Native Gemini Agent Tools Wrappers
def read_pipeline_sheet() -> list[dict]:
    """Connects to the Google Sheet 'VELUSE // Live Inbound Pipeline Database', 
    reads the 'Outbound_Campaign' worksheet, and returns all records as a list of dictionaries.
    
    Returns:
        A list of dictionaries representing the row records in the spreadsheet.
    """
    creds = authenticate_workspace()
    gc = gspread.authorize(creds)
    sheet = gc.open('VELUSE // Live Inbound Pipeline Database').worksheet("Outbound_Campaign")
    return sheet.get_all_records()

def send_outbound_email(to_email: str, subject: str, body_text: str) -> bool:
    """Sends a cold outreach or follow-up email to the target recipient via the Gmail API.
    
    Args:
        to_email: The destination email address.
        subject: The subject header of the outbound email.
        body_text: The plain text message body of the email.
        
    Returns:
        True if the email was successfully transmitted, False otherwise.
    """
    creds = authenticate_workspace()
    gmail_service = build('gmail', 'v1', credentials=creds)
    
    body_html = body_text
    if not body_html.strip().startswith("<html"):
        body_html = f"<html><body><p>{body_html.replace(chr(10), '<br />')}</p></body></html>"
        
    return send_email(gmail_service, to_email, subject, body_html)

def update_lead_status(row_index: int, status: str) -> bool:
    """Updates the primary tracking status cell of a specific row in the Outbound_Campaign 
    spreadsheet and automatically stamps the current date.
    
    Args:
        row_index: The 1-based row index in the spreadsheet.
        status: The new status string to apply (e.g., 'SENT', 'INBOX_WARM', 'OPT_OUT').
        
    Returns:
        True if the update was successful, False otherwise.
    """
    try:
        creds = authenticate_workspace()
        gc = gspread.authorize(creds)
        sheet = gc.open('VELUSE // Live Inbound Pipeline Database').worksheet("Outbound_Campaign")
        headers = [h.lower().strip().replace(" ", "_") for h in sheet.row_values(1)]
        
        status_col = headers.index('touch_1_status') + 1
        date_col = headers.index('touch_1_date') + 1
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        sheet.update_cell(row_index, status_col, status)
        sheet.update_cell(row_index, date_col, today_str)
        return True
    except Exception as e:
        print(f"[-] Failed to update sheet lead status: {e}")
        return False

if __name__ == "__main__":
    execute_sequencer()
