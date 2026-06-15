import os
import os.path
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send'
]

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            cred_file = 'credentials.json'
            if not os.path.exists(cred_file):
                if os.path.exists('credentials.json.json'):
                    cred_file = 'credentials.json.json'
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    gc = gspread.authorize(creds)
    
    try:
        sh = gc.open("VELUSE // Live Inbound Pipeline Database")
        print("Spreadsheet opened successfully!")
        worksheet = sh.worksheet("Outbound_Campaign")
        print("Worksheet Outbound_Campaign found!")
        
        records = worksheet.get_all_records()
        if not records:
            print("No records found. Columns are:")
            print(worksheet.row_values(1))
        else:
            print(f"Total records: {len(records)}")
            print("Columns:")
            print(list(records[0].keys()))
            print("\nFirst 3 records:")
            for idx, r in enumerate(records[:3]):
                print(f"Row {idx+2}: {r}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
