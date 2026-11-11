import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

import json

class GoogleSheetsService:
    def __init__(self, user_creds):
        # Setup authentication using service account credentials
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.spreadsheet_id = user_creds.spreadsheet_id
        
        # Connect to the Google Sheets API if creds json exists
        if user_creds.google_credentials_json:
            try:
                creds_dict = json.loads(user_creds.google_credentials_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    creds_dict, scopes=scopes
                )
                self.service = build('sheets', 'v4', credentials=self.credentials, static_discovery=False)
            except Exception as e:
                self.service = None
                print(f"Google credentials load error: {e}")
        else:
            self.service = None
            print("Google credentials JSON not found in UserCredentials")

    def append_candidate_data(self, candidate_data):
        """
        candidate_data is expected to be a list matching the exact column order of the target Sheet.
        E.g. [name, email, phone, location, qualification, ...]
        """
        if not self.service:
            print("Cannot append to Google Sheets. No service account connected.")
            return False
            
        try:
            sheet = self.service.spreadsheets()
            
            # The A1 notation of a range to search for a logical table of data.
            # Usually appending starting from 'Sheet1!A:K'
            # Update 'Sheet1' if your target tab is named differently.
            range_name = 'Sheet1!A:K'
            
            # Map values
            body = {
                'values': [candidate_data]
            }
            
            result = sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()
            
            print(f"Appended row successfully. Cells updated: {result.get('updates').get('updatedCells')}")
            return True
        except Exception as e:
            print(f"Error appending to Google sheets: {e}")
            return False
