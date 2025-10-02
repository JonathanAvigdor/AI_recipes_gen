from __future__ import print_function
import base64
import os
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    """
    Authenticate and return a Gmail service instance.
    Returns:
        service: Authorized Gmail API service instance.
    """
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
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender: str, to: str, subject: str, message_text: str) -> dict:
    """
    Create a message for an email.
    Args:
        sender (str): Email address of the sender.
        to (str): Email address of the receiver.
        subject (str): Subject of the email.
        message_text (str): Body text of the email.
    Returns:
        dict: A message object ready to send.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}


def send_message(service, user_id: str, message: dict) -> dict:
    """
    Send an email message.
    Args:
        service: Gmail API service instance.
        user_id (str): User ID, usually "me".
        message (dict): Message object created by create_message().
    Returns:
        dict: Sent message metadata.
    """
    sent = service.users().messages().send(userId=user_id, body=message).execute()
    print(f"Message Id: {sent['id']}")
    return sent
