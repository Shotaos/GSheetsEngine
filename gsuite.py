import os.path
import re
import functools
from collections import deque
from pathlib import Path
import io
import os
import backoff
import pathlib
import googleapiclient
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import GOOGLE_APP_CONFIG, TOKEN_FILE

def check_creds(func):
	@functools.wraps(func)
	def wrap(self, *args, **kwargs):
		if not self.creds or not self.creds.valid:
			self.authenticate()
		return func(self, *args, **kwargs)
	return wrap

class GoogleService:
	SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive'
        ]

	def __init__(self):
		self.creds = None


	def authenticate(self):
		if os.path.exists(TOKEN_FILE):
			self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, self.SCOPES)
		else:
			raise PermissionError(f'Google Authorized user file does not exist: {TOKEN_FILE}')

		# If there are no (valid) credentials available, let the user log in.
		if not self.creds or not self.creds.valid:
			if self.creds and self.creds.expired and self.creds.refresh_token:
				self.creds.refresh(Request())

				if not self.creds.valid:
					raise PermissionError(f'Credentials are invalid after refresh')
			else:
				flow = InstalledAppFlow.from_client_config(
				GOOGLE_APP_CONFIG, self.SCOPES)
				self.creds = flow.run_local_server(port=4338)

			# Save the credentials for the next run
			with open(TOKEN_FILE, 'w') as token:
				token.write(self.creds.to_json())

		self.docs = build('docs', 'v1', credentials=self.creds).documents()
		self.sheets = build('sheets', 'v4', credentials=self.creds).spreadsheets()
		self.drive = build('drive', 'v3', credentials=self.creds)

	@check_creds
	def insert_row(self, sheet, row):

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

	@check_creds
	def get_sheet_info(self):
		response = self.sheets.get(
				spreadsheetId=self.spreadsheet_id, fields='sheets/properties').execute()
		return [sheet['properties'] for sheet in response['sheets']]

	def get_sheet_names(self):
		sheets = self.get_sheet_info()
		return [sheet['title'] for sheet in sheets]

	@check_creds
	def get_sheet_data(self, sheet, _range):
		values = self.sheets.values().get(
				spreadsheetId=self.spreadsheet_id, range=sheet + '!' + _range).execute()
		return values['values'][1:]

	@check_creds
	def create_doc(self, name, body):
		response =  self.docs.create(body={'title' : name}).execute()
		return "https://docs.google.com/document/d/" + response['documentId'] + "/edit"

	@check_creds
	def create_folder(self, parent_id, name):

		file_metadata = {
			'name': name,
			'mimeType': 'application/vnd.google-apps.folder',
			'parents': [parent_id]
		}

		folder = self.drive.files().create(
				body=file_metadata, fields='id').execute()

		return folder['id']

	@backoff.on_exception(backoff.expo,
						  googleapiclient.errors.Error,
						  max_tries=4)
	def drive_download_file(self, file_id, local_path):

		request = self.drive.files().get_media(fileId=file_id)

		fh = io.FileIO(local_path, mode='wb')
		downloader = MediaIoBaseDownload(fh, request)
		done = False

		while done is False:
			status, done = downloader.next_chunk()
		return local_path

	def drive_get_folder_contents(self, folder_id):

		q = f"parents = '{folder_id}'"

		page_token = None

		while True:
			response = self.drive.files().list(
				q=q, spaces='drive', fields='nextPageToken, files(id, name, md5Checksum, mimeType)', pageToken=page_token).execute()

			for f in response['files']:
				yield f

			page_token = response.get('nextPageToken')

			if page_token is None:
				break

	@check_creds
	def drive_upload_file(self, parent_id, path):

		file_metadata = {
			'name': os.path.basename(path),
			'parents': [parent_id]
		}

		path = os.path.join(path)
		media = googleapiclient.http.MediaFileUpload(path)

		try:
			return self.drive.files().create(
				body=file_metadata, media_body=media, fields='id').execute()
		except TimeoutError as e:
			print(e)

	@check_creds
	def traverse_drive_recursively(self, folder_id, path):

		root = {
				'id': folder_id,
				'mimeType': 'application/vnd.google-apps.folder',
				'name': '',
				'path': pathlib.Path(path),
		}

		queue = deque([root])

		while queue:
			folder = queue.pop()
			pathlib.Path(folder['path']).mkdir(parents=True, exist_ok=True)

			for _file in self.drive_get_folder_contents(folder['id']):

				_file['path'] = folder['path'] / _file['name']

				if _file['mimeType'] == 'application/vnd.google-apps.folder':
					queue.append(_file)

				elif 'application/vnd.google-apps' not in _file['mimeType']:

					self.drive_download_file(_file['id'], _file['path'])
	

	@check_creds
	def upload_folder(self, path_to_folder, parent_id):
		root_name = os.path.basename(path_to_folder)
		root_id = self.create_folder(parent_id, root_name)

		cache = {}
		cache[path_to_folder] = root_id

		for root, dirs, files in os.walk(path_to_folder, topdown=True):
			parent_dir_id = cache[root]

			for _file in files:
				print("Uploading file: ", _file)
				self.drive_upload_file(parent_dir_id, os.path.join(root, _file))

			for directory in dirs:
				print("Uploading Folder: ", directory)
				_id = self.create_folder(parent_dir_id, directory)
				cache[os.path.join(root, directory)] = _id


class UnrealService(GoogleService):
	def __init__(self, spreadsheet_id):
		super().__init__()
		self.spreadsheet_id = spreadsheet_id
		self.cache = None

	def authenticate(self):
		super().authenticate()
		if self.cache is None:
			self.get_cache()

	def get_cache(self):
		sheets = self.get_sheet_names()
		if not sheets:
			raise ValueError(f"Could not retrive sheet names from Sprreadsheet: {self.spreadsheet_id}")

		sheet = sheets[0]
		self.cache = self.get_sheet_data(sheet, 'A:F')


class NotesService(GoogleService):

	def __init__(self, spreadsheet_id):
		super().__init__()
		self.spreadsheet_id = spreadsheet_id
		self.cache = None

	def authenticate(self):
		super().authenticate()
		if self.cache is None:
			self.get_cache()


	@check_creds
	def search(self, query, sheets=[]):

		result = []

		if self.cache is not None:
			for row in self.cache:
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

		
	@check_creds
	def _create_code_document(self, title, code):
		if code:
			response = self.docs.create(body={"title": 'CODE: ' + title}).execute()
			documentId = response.get('documentId')
			requests = [{"insertText": {"location": {"index": 1}, "text": code}}]
			self.docs.batchUpdate(documentId=documentId, body={"requests": requests}).execute()
			return "https://docs.google.com/document/d/" + documentId + "/edit"
		return

	@check_creds
	def _create_data_document(self, title, youtube, code, quick_text):
		response = self.drive.files().copy(
				fileId='1q69hGvgkZMkpWnjd0PlKO9_PLjkSoS65geUyUuYav-w', body={'name': title}
			).execute()

        # patch the text parts
		requests = [
			{
				"updateTextStyle": {
				"textStyle": {
					"link": {
						"url": youtube if youtube else 'https://youtube.com'
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
						"url": code if code else ' '
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
				'replaceText': title if title else ' ',
				}
            }, 
            {
				'replaceAllText': {
				'containsText': {
					'text': '{{quick_text}}',
					'matchCase':  'true'
				},
				'replaceText': quick_text if quick_text else ' ',
				}
			},
		]

		if not youtube:
			requests.append({
				'replaceAllText': {
				'containsText': {
					'text': '[Youtube link]',
					'matchCase':  'true'
				},
				'replaceText': ' ',
				}
			})

		if not code:
			requests.append({
				'replaceAllText': {
				'containsText': {
					'text': '[Code link]',
					'matchCase':  'true'
				},
				'replaceText': ' ',
				}
			})


		result = self.docs.batchUpdate(
			documentId=response['id'], body={'requests': requests}).execute()


		return "https://docs.google.com/document/d/" + response['id'] + "/edit"
	
	def create_documents(self, data):

		code_url = self._create_code_document(data['title'], data['code'])
		doc_url = self._create_data_document(
				data['title'],
				data['youtube'],
				code_url, data['quick_text'])
		return doc_url, code_url

	@check_creds
	def get_document_text(self, url):

		match = re.search('document/d/([^/]+)', url)
		if not match:
			print(f"Could not parse document url: {url}")
			return

		id_ = match.group(1)
		doc = self.docs.get(documentId=id_).execute()
		return read_strucutural_elements(doc.get('body').get('content'))

	@check_creds
	def get_cache(self):

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

		self.cache = result





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

