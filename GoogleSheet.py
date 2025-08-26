import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from assets import SCOPES
from typing import Union



class GSheetService:
    def __init__(self):
        self.creds = self.get_credentials()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheet = self.service.spreadsheets()

    @staticmethod
    def get_credentials() -> int:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                'ThisNotSecretKeyAtAll/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open('ThisNotSecretKeyAtAll/token.json', 'w') as token:
                token.write(creds.to_json())
            return 1
        except Exception as e:
            print(f"Error in Checking credential : {e}")
            return 0

    def get_credentials(self):
        creds = None
        if os.path.exists('ThisNotSecretKeyAtAll/token.json'):
            creds = Credentials.from_authorized_user_file('ThisNotSecretKeyAtAll/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            raise
        return creds



class GSheetWrite:
    def __init__(self, service, sheet_name, spreadSheetId):
        self.service: GSheetService = service
        self.sheet_name: str = sheet_name
        self.spreadSheetId: str = spreadSheetId


    def write_to_gsheet(self, data: Union[str, list]):
        try:
            if isinstance(data, str):
                values = [[data]] # [[data]]
            elif isinstance(data, list):
                values = data # [["data1", "data2"], ["data3", "data4"]]
           
            body = {"values": values}
            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheetId,
                    range=self.range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            
            return result
        except HttpError as err:

            return
    