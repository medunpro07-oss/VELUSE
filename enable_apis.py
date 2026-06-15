import os
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform'
]

def main():
    creds = None
    token_file = 'C:/Users/sajme/OneDrive/Desktop/VELUSE AGENCY/token_mgmt.json'
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}. Re-authenticating.")
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/sajme/OneDrive/Desktop/VELUSE AGENCY/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    service = build('serviceusage', 'v1', credentials=creds)
    project_id = 'project-donna-497203'
    
    apis = [
        "bigquery.googleapis.com",
        "bigquerydatatransfer.googleapis.com",
        "dataform.googleapis.com",
        "sheets.googleapis.com",
        "gmail.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "iam.googleapis.com",
        "serviceusage.googleapis.com",
        "storage.googleapis.com",
        "secretmanager.googleapis.com",
        "logging.googleapis.com",
        "monitoring.googleapis.com",
        "places.googleapis.com"
    ]
    
    for api in apis:
        print(f"Enabling {api}...")
        try:
            operation = service.services().enable(
                name=f"projects/{project_id}/services/{api}"
            ).execute()
            print(f"Operation started for {api}: {operation.get('name')}")
            
            op_service = service.operations()
            while True:
                status = op_service.get(name=operation.get('name')).execute()
                if status.get('done'):
                    if 'error' in status:
                        print(f"Error enabling {api}: {status['error']}")
                    else:
                        print(f"Successfully enabled {api}!")
                    break
                time.sleep(2)
        except Exception as e:
            print(f"Exception enabling {api}: {e}")

if __name__ == '__main__':
    main()
