import os
import json
from pathlib import Path
from sheets import GoogleSheets
from qt5.ui import alert_dialog, AddRecordUI
from qt5.workers import GoogleServiceWorker
from config import SETTINGS_FILE, TOPICS_FILE

class SheetsController():
    def __init__(self, view, settings):
        self._view = view
        self._settings_view = settings
        self._init_settings()
        self._check_login()
        self._view.add_table_columns(['Title', 'Cateogry', 'Code'])
        # Connect signals and slots
        self._connectSignals()
        self.data = None

    def _init_settings(self):
        if os.path.isfile(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                try:
                    self.settings = json.load(f)
                except json.JSONDecodeError:
                    self.settings = {"sheetId": "", "excludeSheets" : []}
        else:
            self.settings = {"sheetId": "", "excludeSheets" : []}

    def _update_settings(self):
        self.settings = self._settings_view.get_settings()
        self._save_settings()

        # activate startup will reinitialize sheets throughout the UI
        self._activate_startup()

    def _open_settings_dialog(self):
        self._settings_view.set_settings(self.settings, self._sheets)
        self._settings_view.show()

    def _save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

    def _check_login(self):
        self._view.start_spinner()

        gservice = GoogleSheets(self.settings['sheetId'])
        if not gservice.check_credentials():
            alert_dialog()
            self.login_worker = GoogleServiceWorker(self.settings['sheetId'], "login")
            self.login_worker.log.connect(self._logger)
            self.login_worker.recordsDone.connect(self._activate_startup)
            self.login_worker.start()
        else:
            self._activate_startup()

    def _activate_startup(self, arg=None):
        self._view.start_spinner()
        self.worker = GoogleServiceWorker(self.settings['sheetId'], "get_sheets")
        self.worker.log.connect(self._logger)
        self.worker.recordsDone.connect(self._init_topics)
        self.worker.start()

    def _handle_search(self):
        query = self._view.get_search_text()

        if query:
            self._view.start_spinner()
            #topics = self._view.get_checked_topics()
            #topics = topics if topics != [] else [s for s in self._sheets if s not in self.settings['excludeSheets']]
            topics = [s for s in self._sheets if s not in self.settings['excludeSheets']]
            self.worker = GoogleServiceWorker(self.settings['sheetId'], "search", (query, topics))
            self.worker.log.connect(self._logger)
            self.worker.recordsDone.connect(self._add_rows)
            self.worker.start()

    def _add_rows(self, rows):
        self.data = rows
        self._update_rows()

    def _update_rows(self):

        self._view.clear_table()
        current_topics = [_.lower() for _ in self._view.get_checked_topics()]

        open(TOPICS_FILE, 'w').write(json.dumps(current_topics, indent=4))

        self._settings_view.set_setting('activeTopics', current_topics)
        self._save_settings()

        if self.data:
            for row in self.data:
                topic, category, title, link, code_link = row
                category = f'[{topic}] ' + category
                if current_topics == [] or topic.lower() in current_topics:
                    self._view.addRow([title, category, code_link], link)
        self._view.stop_spinner()

        
    def _init_topics(self, sheets):
        self._sheets = sheets
        filtered_sheets = [sheet for sheet in sheets if sheet not in self.settings['excludeSheets']]

        try:
            active_topics = json.loads(open(TOPICS_FILE, 'r').read())
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            active_topics = []

        self._view.add_topic_buttons(filtered_sheets, active_topics)
        self._settings_view.set_settings(self.settings, sheets)
        #self._view.populate_topic_dropdowns(filtered_sheets)
        self._view.stop_spinner()

    def _handle_add_record(self):
        sheet = self._view.get_topic_text()
        category = self._view.get_category_text()
        title = self._view.get_title_text()

        # clear the category & title fields
        self._view.clear_fields()
        self._view.start_spinner()

        self.worker = GoogleServiceWorker(self.settings['sheetId'], "create_doc", (sheet, category, title))
        self.worker.log.connect(self._logger)
        self.worker.recordsDone.connect(self._add_rows)
        self.worker.start()
        
    def _navigate_to_sheet(self):
        self.worker = GoogleServiceWorker(self.settings['sheetId'], "open_sheet")
        self.worker.start()

    def handle_add_record(self):
        topics = [s for s in self._sheets if s not in self.settings['excludeSheets']]
        record = AddRecordUI(topics)
        status = record.exec_()
        if status:
            data = record.get_data()
            self.worker = GoogleServiceWorker(self.settings['sheetId'], "create_doc", data)
            self.worker.log.connect(self._logger)
            self.worker.recordsDone.connect(self._add_rows)
            self._view.start_spinner()
            self.worker.start()

    def copy_code(self, url):
        self._view.start_spinner()
        self.worker = GoogleServiceWorker(self.settings['sheetId'], "get_copy", url)
        self.worker.log.connect(self._logger)
        self.worker.codeDone.connect(self.copy_code_to_clipboard)
        self.worker.start()

    def copy_code_to_clipboard(self, code):
        if code:
            self._view.copy_to_clipboard(code)
        self._view.stop_spinner()

    def refresh_cache(self):
        self._view.start_spinner()
        self.worker = GoogleServiceWorker(self.settings['sheetId'], "refresh_cache", None)
        self.worker.log.connect(self._logger)
        self.worker.recordsDone.connect(self.refresh_done)
        self.worker.start()
    
    def refresh_done(self, def_list = []):
        self._view.stop_spinner()
        

    def _connectSignals(self):
        self._view.search_button.clicked.connect(self._handle_search)
        #self._view.add_record.clicked.connect(self._handle_add_record)
        self._view.settings_button.clicked.connect(self._open_settings_dialog)
        self._settings_view.okButton.clicked.connect(self._update_settings)
        self._view.open_sheet_button.clicked.connect(self._navigate_to_sheet)
        self._view.add_new_button.clicked.connect(self.handle_add_record)
        self._view.filtersChanged.connect(self._update_rows)
        self._view.copy.connect(self.copy_code)
        self._view.refresh.clicked.connect(self.refresh_cache)

    def _logger(self, msg):
        self._view.set_log_message(msg)
