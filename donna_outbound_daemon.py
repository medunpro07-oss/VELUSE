import os
import time
import base64
from email.mime.text import MIMEText
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_gmail_service(creds):
    return build('gmail', 'v1', credentials=creds)

def send_email(service, recipient, subject, body):
    message = MIMEText(body)
    message['to'] = recipient
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return True
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")
        return False

def main():
    print("[*] INITIALIZING GOOGLE WORKSPACE DAEMON ENGINE...")
    
    workspace_root = "C:/Users/sajme/OneDrive/Desktop/VELUSE AGENCY"
    token_path = os.path.join(workspace_root, "token.json")
    creds_path = os.path.join(workspace_root, "credentials.json")
    
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[*] Refreshing expired credentials token...")
            creds.refresh(Request())
        else:
            print("[*] Initiating InstalledAppFlow authorization...")
            if not os.path.exists(creds_path):
                print(f"[!] Critical Error: credentials.json not found at {creds_path}")
                return
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
            print("[*] Credentials token cached successfully.")

    # Authorize Sheets
    gc = gspread.authorize(creds)
    # Build Gmail service
    gmail_service = get_gmail_service(creds)
    
    try:
        sh = gc.open("VELUSE // Live Inbound Pipeline Database")
        worksheet = sh.worksheet("Outbound_Campaign")
        print("[+] Outbound_Campaign worksheet loaded successfully.")
    except Exception as e:
        print(f"[!] Error loading spreadsheet: {e}")
        return

    records = worksheet.get_all_records()
    if not records:
        print("[-] No records found in Outbound_Campaign sheet.")
        return
        
    print(f"[*] Sweeping {len(records)} pipeline entries...")
    
    # Locate headers dynamically to accommodate minor formatting discrepancies
    headers = [h.strip().lower() for h in worksheet.row_values(1)]
    
    col_map = {
        'status': headers.index('status') + 1 if 'status' in headers else None,
        'variant': headers.index('variant') + 1 if 'variant' in headers else None,
        'email': headers.index('email') + 1 if 'email' in headers else (headers.index('emails') + 1 if 'emails' in headers else None),
        'business': headers.index('business name') + 1 if 'business name' in headers else (headers.index('name') + 1 if 'name' in headers else None),
        'website': headers.index('website') + 1 if 'website' in headers else None
    }
    
    if not col_map['status'] or not col_map['email']:
        print("[!] Critical: Status or Email column could not be mapped.")
        return

    # Process pending outbound messages
    for i, row in enumerate(records):
        row_num = i + 2  # 1-indexed and skipping header row
        
        # Safe extraction
        status_val = str(row.get('Status', '')).strip().upper()
        variant_val = str(row.get('Variant', 'A')).strip().upper()
        email_val = str(row.get('Email', row.get('Emails', ''))).strip()
        biz_name = str(row.get('Business Name', row.get('Name', 'Valued Partner'))).strip()
        website_val = str(row.get('Website', 'your site')).strip()

        if status_val == 'PENDING' and email_val:
            print(f"[*] Processing row {row_num} | Target: {email_val} | Variant: {variant_val}")
            
            # Formulate text-based pattern-interrupt templates
            if variant_val == 'B':
                subject = f"System Leakage Audit // {biz_name}"
                body = (
                    f"Hey,\n\n"
                    f"Ran an audit scan on {website_val} and detected structural leakage in your patient acquisition tracking. "
                    f"Are you open to fixing this leakage to secure another $10K/mo?\n\n"
                    f"Donna Paulsen\nChief of Staff, Veluse Agency"
                )
            else:
                subject = f"Capacity Inquiry // {biz_name}"
                body = (
                    f"Hey,\n\n"
                    f"Noticed you offer elite aesthetic services at {biz_name}. "
                    f"Do you have the system capacity to handle an extra 20-30 high-ticket patients this month?\n\n"
                    f"Donna Paulsen\nChief of Staff, Veluse Agency"
                )

            # Send Email
            success = send_email(gmail_service, email_val, subject, body)
            if success:
                # Update status in Sheet
                status_str = f"SENT: VARIANT {variant_val}"
                worksheet.update_cell(row_num, col_map['status'], status_str)
                print(f"[+] Outbound transaction complete: {status_str}")
            else:
                print(f"[-] Outbound transaction failed for {email_val}")
            
            # Anti-spam deliverability delay
            time.sleep(3)

    print("\n[ WORKSPACE_FULLY_AUTONOMOUS ]")

if __name__ == '__main__':
    main()
