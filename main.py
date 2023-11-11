from __future__ import print_function

import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

count = 0
def download_pdfs(service, label, start_date, end_date):
    query = f"label:{label} after:{start_date} before:{end_date}"
    page_token = None

    while True:
        results = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
        messages = results.get('messages', [])

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            payload = msg['payload']

            if 'parts' in payload:
                parts = payload['parts']
                for part in parts:
                    if part['mimeType'] == "application/pdf":
                        filename = part['filename']

                        if 'data' in part['body']:
                            file_data = base64.urlsafe_b64decode(part['body']['data'])
                        else:
                            attachment_id = part['body']['attachmentId']
                            attachment = service.users().messages().attachments().get(
                                userId='me', messageId=message['id'], id=attachment_id).execute()
                            file_data = base64.urlsafe_b64decode(attachment['data'])
                        global count
                        with open(f'{count}-{filename}', 'wb') as f:
                            f.write(file_data)

                            count += 1
                            print(f"Downloaded {filename}")

        page_token = results.get('nextPageToken')
        if not page_token:
            break
def authenticate():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds



if __name__ == '__main__':
    # label = "raif"
    # start_date = "2023-01-01"
    # end_date = "2023-12-12"
    label = "yettel"
    start_date = "2023-01-01"
    end_date = "2023-12-12"

    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    download_pdfs(service, label, start_date, end_date)