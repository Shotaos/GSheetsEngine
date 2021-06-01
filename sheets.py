import os.path
import re
from pathlib import Path
from pprint import pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import GOOGLE_APP_CONFIG


TOKEN_DIR= Path.home() / ".sheetsearch"
TOKEN_DIR.mkdir(exist_ok=True)


class GoogleSheets():
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/documents']

	def __init__(self, spreadsheet_id):
		self.spreadsheet_id = spreadsheet_id
		self.creds = None

	def check_credentials(self):
		if os.path.exists(TOKEN_DIR / 'token.json'):
		    creds = Credentials.from_authorized_user_file(TOKEN_DIR / 'token.json', self.SCOPES)
		else:
			return False

		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())

				# Check validity after refresh
				if not creds.valid:
					return False
			else:
				return False
		return True

	def login(self):
		self.__init_service()
	
	def __check_creds_validity(self):
		if not self.creds or not self.creds.valid:
			self.__init_service()

	def __init_service(self):
		creds = None
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists(TOKEN_DIR / 'token.json'):
		    creds = Credentials.from_authorized_user_file(TOKEN_DIR / 'token.json', self.SCOPES)

		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
		    if creds and creds.expired and creds.refresh_token:
			    creds.refresh(Request())
		    else:
			    flow = InstalledAppFlow.from_client_config(
			    GOOGLE_APP_CONFIG, self.SCOPES)
			    creds = flow.run_local_server(port=4338)

		    # Save the credentials for the next run
		    with open(TOKEN_DIR / 'token.json', 'w') as token:
			    token.write(creds.to_json())

		self.creds = creds
		self.docs = build('docs', 'v1', credentials=creds).documents()
		self.sheets = build('sheets', 'v4', credentials=creds).spreadsheets()

	def get_sheet_info(self):
		self.__check_creds_validity()

		response = self.sheets.get(spreadsheetId=self.spreadsheet_id, fields='sheets/properties').execute()
		return [sheet['properties'] for sheet in response['sheets']]

	def get_sheet_names(self):
		self.__check_creds_validity()

		sheets = self.get_sheet_info()
		return [sheet['title'] for sheet in sheets]

	def get_sheet_data(self, sheet):
		self.__check_creds_validity()

		values = self.sheets.values().get(spreadsheetId=self.spreadsheet_id, range=sheet + '!A:C').execute()
		return values['values'][1:]

	
	def search(self, query, sheets=[]):
		self.__check_creds_validity()

		result = []
		# Get sheet names
		sheets = sheets if sheets else self.get_sheet_names()
		# Build the ranges expression ["sheet1!A:C", "sheet2!A:C", "sheet3!A:C"]
		ranges = [sheet + '!A:D' for sheet in sheets]

		values = self.sheets.values().batchGet(spreadsheetId=self.spreadsheet_id, ranges=ranges).execute()

		for sheet in values['valueRanges']:
			if sheet.get('values'):
				sheet_name = sheet['range'].split('!')[0]

				for row in sheet['values'][1:]:
					
					# Only category is given.
					if len(row) < 2:
						continue

					if re.search(query, row[1], re.IGNORECASE):
						link = '' if len(row) < 3 else row[2]
						result.append([sheet_name, row[0], row[1], link])
					
		return result[::-1]

	def insert_row(self, sheet, row):
		self.__check_creds_validity()

		body = {'majorDimension': 'ROWS',
			'values': [row]}
		request = self.sheets.values().append(spreadsheetId=self.spreadsheet_id,
							valueInputOption="RAW",
							range=sheet + '!A:C',
							body=body)
		return request.execute()
		

	def create_doc(self, name):
		self.__check_creds_validity()

		response =  self.docs.create(body={'title' : name}).execute()
		return "https://docs.google.com/document/d/" + response['documentId'] + "/edit"
