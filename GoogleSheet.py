import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import GoogleAuthError
import sys

from settings import SCOPES
from typing import Union, Optional, Dict, Any



class GSheetService:
    def __init__(self):
        try:
            self.creds = self.get_credentials()
            self.service = build('sheets', 'v4', credentials=self.creds)
            self.sheet = self.service.spreadsheets()
        except GoogleAuthError:
            self.creds = None
            self.service = None
            self.sheet = None
        except Exception:
            self.creds = None
            self.service = None
            self.sheet = None

    def is_sheet_exists(self, spreadSheetId: str, title: str):
        """
        Traverse through metadata of the spreadsheet to look for sheet title.
        """
        try:
            spreadsheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=spreadSheetId,
                fields="sheets.properties"
            ).execute()

            is_sheet_exists = False
            if "sheets" in spreadsheet_metadata:
                for sheet in spreadsheet_metadata["sheets"]:
                    if "properties" in sheet and "title" in sheet["properties"]:
                        if sheet["properties"]["title"] == title:
                            is_sheet_exists = True

            return is_sheet_exists
        except Exception as e:
            print(f"Error {e}")


    def check_last_value_in_column(self, spreadSheetId: str, range_name:str) -> int:
        """
        Check the last value in the column
        If not hit the last row, return 2
        If hit the last row, return the next empty row
        """
        try:
            _result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadSheetId, range=range_name)
                .execute()
                )

            _values = _result.get('values', [])

            last_row_index = -1 # Flag for not hit the last row
            for i in reversed(range(len(_values))):
                if _values[i] and _values[i][0].strip():  # if not empty or just spaces
                    last_row_index = i # Because we start from row i in the sheet
                    break
            return last_row_index
        except Exception as e:
            return -1

    def get_credentials(self) -> Credentials:
        creds = None
        # Load existing credentials if available
        if os.path.exists('ThisNotSecretKeyAtAll/token.json'):
            creds = Credentials.from_authorized_user_file('ThisNotSecretKeyAtAll/token.json', SCOPES)
        if sys.platform.startswith('win'):
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'ThisNotSecretKeyAtAll/credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                
        else:
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'ThisNotSecretKeyAtAll/credentials.json', SCOPES)
                    creds = flow.run_console()
        # Save the credentials for the next run
        if creds:
            with open('ThisNotSecretKeyAtAll/token.json', 'w') as token:
                token.write(creds.to_json())
            
        return creds

class GSheetWrite:
    def __init__(self, gservice, sheet_name: str = None, spreadSheetId: str = None):
        self.gservice: GSheetService = gservice
        self.sheet_name: str = sheet_name
        self.spreadSheetId: str = spreadSheetId

    def write_to_gsheet(self, data: Union[str, list], range_name: str) -> Optional[Dict[str, Any]]:
        try:
            if isinstance(data, str):
                values = [[data]] # [[data]]
            elif isinstance(data, list):
                values = data # [["data1", "data2"], ["data3", "data4"]]
           
            body = {"values": values}
            result = (
                self.gservice.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadSheetId,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            return result
        except HttpError as e:
            print(f"Error {e}")
            return
        except Exception as e:
            print(f"Error {e}")
            return
        
    def create_new_spreadsheet(self, title) -> int:
        # creds = self.service.service
        try:
            spreadsheet = {"properties": {"title": title}}
            spreadsheet = (
                self.gservice.service.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId")
                .execute()
            )
            print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")

            return spreadsheet.get("spreadsheetId")
        except HttpError as e:
            print(f"Error {e}")
            return

    def create_new_sheet(self, title) -> int:
        if self.gservice.is_sheet_exists(self.spreadSheetId, title):
            return 1  # Sheet already exists
        # Init request body
        try:
            body = {
                "requests": {
                    "addSheet": {
                        "properties": {
                            "title": title
                        }
                    }
                }
            }

            self.gservice.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadSheetId, body=body).execute()
            return 1
        except HttpError as e:
            print(f"Error {e}")
            return 0