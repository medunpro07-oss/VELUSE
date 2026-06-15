import os
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send'
]

def main():
    creds = None
    token_path = 'C:/Users/sajme/OneDrive/Desktop/VELUSE AGENCY/token.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/sajme/OneDrive/Desktop/VELUSE AGENCY/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    gc = gspread.authorize(creds)
    try:
        sh = gc.open("VELUSE // Live Inbound Pipeline Database")
        print("SPREADSHEET_OPENED")
        worksheet = sh.worksheet("Outbound_Campaign")
        records = worksheet.get_all_records()
        print(f"Total rows: {len(records)}")
        if records:
            print("First row keys:", list(records[0].keys()))
            print("First row values:", records[0])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
