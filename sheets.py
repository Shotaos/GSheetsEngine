import os.path
import re
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import GOOGLE_APP_CONFIG, TOKEN_FILE
from docs_template import DOCS_TEMPLATE_JSON


class GoogleSheets():
	SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive'
        ]
	cache = None

	def __init__(self, spreadsheet_id):
		self.spreadsheet_id = spreadsheet_id
		self.creds = None

	def check_credentials(self):
		if os.path.exists(TOKEN_FILE):
		    creds = Credentials.from_authorized_user_file(TOKEN_FILE, self.SCOPES)
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
		if os.path.exists(TOKEN_FILE):
		    creds = Credentials.from_authorized_user_file(TOKEN_FILE, self.SCOPES)

		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
		    if creds and creds.expired and creds.refresh_token:
			    creds.refresh(Request())
		    else:
			    flow = InstalledAppFlow.from_client_config(
			    GOOGLE_APP_CONFIG, self.SCOPES)
			    creds = flow.run_local_server(port=4338)

		    # Save the credentials for the next run
		    with open(TOKEN_FILE, 'w') as token:
			    token.write(creds.to_json())

		self.creds = creds
		self.docs = build('docs', 'v1', credentials=creds).documents()
		self.sheets = build('sheets', 'v4', credentials=creds).spreadsheets()
		self.drive = build('drive', 'v3', credentials=creds)


		if GoogleSheets.cache is None:
			self.get_cache()

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

		if GoogleSheets.cache is not None:
			for row in GoogleSheets.cache:
				if not sheets or row[0].lower() in [_.lower() for _ in sheets]:
					if re.search(query, row[2], re.IGNORECASE):
						result.append(row)
			return result

		# Get sheet names
		sheets = sheets if sheets else self.get_sheet_names()
		# Build the ranges expression ["sheet1!A:C", "sheet2!A:C", "sheet3!A:C"]
		ranges = [sheet + '!A:D' for sheet in sheets]

		values = self.sheets.values().batchGet(spreadsheetId=self.spreadsheet_id, ranges=ranges).execute()

		for sheet in values['valueRanges']:
			if sheet.get('values'):
				sheet_name = sheet['range'].split('!')[0]

				# remove unnecessary quote signs
				if sheet_name.startswith("'") and sheet_name.endswith("'"):
					sheet_name = sheet_name[1:-1]

				for row in sheet['values'][1:]:
					
					# Only category is given.
					if len(row) < 2:
						continue

					if re.search(query, row[1], re.IGNORECASE):
						link = '' if len(row) < 3 else row[2]
						code_link = '' if len(row) < 4 else row[2]
						result.append([sheet_name, row[0], row[1], link, code_link])
					
		return result[::-1]

	def insert_row(self, sheet, row):
		self.__check_creds_validity()

		body = {'majorDimension': 'ROWS',
			'values': [row]}
		request = self.sheets.values().append(spreadsheetId=self.spreadsheet_id,
							valueInputOption="RAW",
							range=sheet + '!A:C',
							body=body)
		result = request.execute()
		# Update cache
		self.get_cache()
		return result
		
	def _create_code_document(self, title, code):
		response = self.docs.create(body={"title": 'CODE: ' + title}).execute()
		documentId = response.get('documentId')
		requests = [{"insertText": {"location": {"index": 1}, "text": code}}]
		self.docs.batchUpdate(documentId=documentId, body={"requests": requests}).execute()
		return "https://docs.google.com/document/d/" + documentId + "/edit"

	def _create_data_document(self, title, youtube, code, quick_text):
		response = self.drive.files().copy(
				fileId='1q69hGvgkZMkpWnjd0PlKO9_PLjkSoS65geUyUuYav-w', body={'title': title}
			).execute()

        # patch the text parts
		requests = [
            {
                "updateTextStyle": {
                "textStyle": {
                    "link": {
                        "url": youtube
                    }
                },
                "range": {
                    "startIndex": 12,
                    "endIndex": 24
                },
                "fields": "link"
                }
            },
            {
                "updateTextStyle": {
                "textStyle": {
                    "link": {
                        "url": code
                    }
                },
                "range": {
                    "startIndex": 26,
                    "endIndex": 35
                },
                "fields": "link"
                }
            },
			{
				'replaceAllText': {
				'containsText': {
					'text': '{{title}}',
					'matchCase':  'true'
				},
				'replaceText': title,
				}
            }, 
            {
				'replaceAllText': {
				'containsText': {
					'text': '{{quick_text}}',
					'matchCase':  'true'
				},
				'replaceText': quick_text,
				}
			},
		]

		result = self.docs.batchUpdate(
			documentId=response['id'], body={'requests': requests}).execute()


		return "https://docs.google.com/document/d/" + response['id'] + "/edit"
	
	def create_documents(self, data):
		self.__check_creds_validity()

		code_url = self._create_code_document(data['title'], data['code'])
		doc_url = self._create_data_document(
				data['title'],
				data['youtube'],
				code_url, data['quick_text'])
		return doc_url, code_url

	def get_document_text(self, url):
		self.__check_creds_validity()

		match = re.search('document/d/([^/]+)', url)
		if not match:
			print(f"Could not parse document url: {url}")
			return

		id_ = match.group(1)
		doc = self.docs.get(documentId=id_).execute()
		return read_strucutural_elements(doc.get('body').get('content'))

	def get_cache(self):
		self.__check_creds_validity()

		result = []
		# Get sheet names
		sheets = self.get_sheet_names()
		# Build the ranges expression ["sheet1!A:C", "sheet2!A:C", "sheet3!A:C"]
		ranges = [sheet + '!A:D' for sheet in sheets]

		values = self.sheets.values().batchGet(spreadsheetId=self.spreadsheet_id, ranges=ranges).execute()

		for sheet in values['valueRanges']:
			if sheet.get('values'):
				sheet_name = sheet['range'].split('!')[0]

				# remove unnecessary quote signs
				if sheet_name.startswith("'") and sheet_name.endswith("'"):
					sheet_name = sheet_name[1:-1]

				for row in sheet['values'][1:]:
					# Only category is given.
					if len(row) < 2:
						continue

					link = '' if len(row) < 3 else row[2]
					code_link = '' if len(row) < 4 else row[3]
					result.append([sheet_name, row[0], row[1], link, code_link])

		GoogleSheets.cache = result



	def create_doc(self, name, body):
		self.__check_creds_validity()

		response =  self.docs.create(body={'title' : name}).execute()
		return "https://docs.google.com/document/d/" + response['documentId'] + "/edit"

# helper functions

def read_strucutural_elements(elements):
	"""Recurses through a list of Structural Elements to read a document's text where text may be
		in nested elements.

		Args:
			elements: a list of Structural Elements.
	"""
	text = ''
	for value in elements:
		if 'paragraph' in value:
			elements = value.get('paragraph').get('elements')
			for elem in elements:
				text += read_paragraph_element(elem)
		elif 'table' in value:
			# The text in table cells are in nested Structural Elements and tables may be
			# nested.
			table = value.get('table')
			for row in table.get('tableRows'):
				cells = row.get('tableCells')
				for cell in cells:
					text += read_strucutural_elements(cell.get('content'))
		elif 'tableOfContents' in value:
			# The text in the TOC is also in a Structural Element.
			toc = value.get('tableOfContents')
			text += read_strucutural_elements(toc.get('content'))
	return text

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')

