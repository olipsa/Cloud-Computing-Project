from __future__ import print_function

import base64
import mimetypes
import os.path
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import *

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = ['https://mail.google.com/']


def get_service():
    try:
        creds = Credentials.from_authorized_user_info(GMAIL_TOKEN_CREDENTIALS, SCOPES)
    except ValueError:
        creds = None
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                GMAIL_TOKEN, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        # with open('token.json', 'w') as token:
        #     token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        return service

    except HttpError as error:
        print(f'An error occurred: {error}')


def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id,
                                                  body=message).execute()
        return message
    except Exception as e:
        print('An error occurred: {}'.format(e))
        return None


def create_message(
        sender,
        to,
        subject,
        message_text,
        attachment
):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)
    if attachment is not None:
        content_type, encoding = mimetypes.guess_type(attachment)
        main_type, sub_type = content_type.split('/', 1)
        file_name = os.path.basename(attachment)
        f = open(attachment, 'rb')
        myfile = MIMEBase(main_type, sub_type)
        myfile.set_payload(f.read())
        myfile.add_header('Content-Disposition', 'attachment', filename=file_name)
        encoders.encode_base64(myfile)

        f.close()
        message.attach(myfile)
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    else:
        raw_message = \
            base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()
    return {'raw': raw_message}
