import os.path
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GoogleSheets():
	SPREADSHEET_ID = '11IETLAULJA1NpDuRWp7WtnNbvAhIcJKuJNJ-N6vYMm4'
	SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/documents']

	def __init__(self):
		self.__init_service()

	def __init_service(self):
		creds = None
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists('token.json'):
		    creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
		    if creds and creds.expired and creds.refresh_token:
			    creds.refresh(Request())
		    else:
			    flow = InstalledAppFlow.from_client_secrets_file(
			    'credentials.json', self.SCOPES)
			    creds = flow.run_local_server(port=4338)

		    # Save the credentials for the next run
		    with open('token.json', 'w') as token:
			    token.write(creds.to_json())

		self.docs = build('docs', 'v1', credentials=creds).documents()
		self.sheets = build('sheets', 'v4', credentials=creds).spreadsheets()

	def get_sheet_info(self):
		response = self.sheets.get(spreadsheetId=self.SPREADSHEET_ID, fields='sheets/properties').execute()
		return [sheet['properties'] for sheet in response['sheets']]

	def get_sheet_names(self):
		sheets = self.get_sheet_info()
		return [sheet['title'] for sheet in sheets]

	def get_sheet_data(self, sheet):
		values = self.sheets.values().get(spreadsheetId=self.SPREADSHEET_ID, range=sheet + '!A:C').execute()
		return values['values'][1:]

	
	def search(self, query, sheets=[]):
		result = []

		# Get sheet names
		sheets = sheets if sheets else self.get_sheet_names()
		# Build the ranges expression ["sheet1!A:C", "sheet2!A:C", "sheet3!A:C"]
		ranges = [sheet + '!A:C' for sheet in sheets]

		values = self.sheets.values().batchGet(spreadsheetId=self.SPREADSHEET_ID, ranges=ranges).execute()

		for sheet in values['valueRanges']:
			sheet_name = sheet['range'].split('!')[0]
			for row in sheet['values'][1:]:
				if re.search(query, row[0] + ' ' + row[1], re.IGNORECASE):
					result.append([sheet_name] + row)
					
		return result

	def insert_row(self, sheet, row):
		body = {'majorDimension': 'ROWS',
			'values': [row]}
		request = self.sheets.values().append(spreadsheetId=self.SPREADSHEET_ID,
							valueInputOption="RAW",
							range=sheet + '!A:C',
							body=body)
		return request.execute()
		

	def create_doc(self, name):
		response =  self.docs.create(body={'title' : name}).execute()
		return "https://docs.google.com/document/d/" + response['documentId'] + "/edit"