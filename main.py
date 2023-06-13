from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import re
import unsubscribe

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
"""
Lists the user's Gmail labels.
    """

unsubscribeEmails = {}


def listLabels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    if not labels:
        print('No labels found.')
        return
    print('Labels:')
    for label in labels:
        print(label['name'])


def getUnsubscribeLink(email_headers):
    for header in email_headers:
        type_ = header['name']
        if type_ == 'List-Unsubscribe':
            unsubscribeHeaderValue = header['value']
            unsubscribeLinks = re.findall(r'<.*?>', unsubscribeHeaderValue)
            if "mailto" not in unsubscribeLinks[0]:
                unsubscribeLinks[0] = unsubscribeLinks[0].strip("<>")
                return unsubscribeLinks[0]


def getSenderAddress(email_headers):
    for header in email_headers:
        type_ = header['name']
        if type_ == 'From':
            sender = header['value']
            if sender is not None:
                # print("got address")
                return sender


def retrieveEmails(service):
    results = service.users().messages().list(userId='me', labelIds=['CATEGORY_PROMOTIONS'], maxResults=20).execute()
    messages = results.get('messages', [])

    if not messages:
        print("Messages not retrieved")
        return

    for message in messages:
        message = service.users().messages().get(userId='me', id=message['id']).execute()
        email_headers = message['payload']['headers']
        sender = getSenderAddress(email_headers)

        if sender not in unsubscribeEmails:
            unsubscribeLink = getUnsubscribeLink(email_headers)
            if unsubscribeLink is None:
                print(sender + " doesn't have easily findable link")
                msg_to_be_deleted = service.users().messages().trash(userId='me', id=message['id']).execute()
                continue

            # unsubbing process
            unsubscribe.unsubscribe(unsubscribeLink)

            # add to a dictionary so, we don't repeat work
            unsubscribeEmails[sender] = unsubscribeLink

        msg_to_be_deleted = service.users().messages().trash(userId = 'me', id = message['id']).execute()

"""authorizing the user"""


def authorize():
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


def main():
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=authorize())

        retrieveEmails(service=service)
        for k, v in unsubscribeEmails.items():
            print(k, v)
            # if unsubscribeEmails.get(k) is None:
            #     continue
            # if unsubscribe.unsubscribe(unsubscribeEmails.get(k)) == 0:
            #     return 0
                # function to move email to trash

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
