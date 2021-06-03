import os
import json
from pathlib import Path
from sheets import GoogleSheets
from qt5.ui import alert_dialog
from qt5.workers import GoogleServiceWorker

SETTINGS_DIR= Path.home() / ".sheetsearch"
SETTINGS_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = SETTINGS_DIR / 'sheetsettings.json'

class SheetsController():
    def __init__(self, view, settings):
        self._view = view
        self._settings_view = settings
        self._init_settings()
        self._check_login()
        self._view.add_table_columns(['Title', 'Cateogry', 'Topic'])
        # Connect signals and slots
        self._connectSignals()

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
            topics = self._view.get_checked_topics()
            topics = topics if topics != [] else [s for s in self._sheets if s not in self.settings['excludeSheets']]
            self.worker = GoogleServiceWorker(self.settings['sheetId'], "search", (query, topics))
            self.worker.log.connect(self._logger)
            self.worker.recordsDone.connect(self._add_rows)
            self.worker.start()

    def _add_rows(self, rows):
        self._view.clear_table()
        if rows:
            for row in rows:
                topic, category, title, link = row
                self._view.addRow([title, category, topic], link)
        self._view.stop_spinner()

        
    def _init_topics(self, sheets):
        self._sheets = sheets
        filtered_sheets = [sheet for sheet in sheets if sheet not in self.settings['excludeSheets']]
        self._view.add_topic_checkboxes(filtered_sheets)
        self._settings_view.set_settings(self.settings, sheets)
        self._view.populate_topic_dropdowns(filtered_sheets)
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
        


    def _connectSignals(self):
        self._view.search_button.clicked.connect(self._handle_search)
        self._view.add_record.clicked.connect(self._handle_add_record)
        self._view.settings_button.clicked.connect(self._open_settings_dialog)
        self._settings_view.okButton.clicked.connect(self._update_settings)

    def _logger(self, msg):
        self._view.set_log_message(msg)
