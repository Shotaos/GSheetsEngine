import webbrowser
from sheets import GoogleSheets
from qt5.ui import alert_dialog
from qt5.workers import GoogleServiceWorker

class SheetsController():
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self._check_login()
        self._view.add_table_columns(['Title', 'Cateogry', 'Topic'])
        # Connect signals and slots
        self._connectSignals()


    def _check_login(self):
        self._view.start_spinner()

        gservice = GoogleSheets()
        if not gservice.check_credentials():
            alert_dialog()
            self.login_worker = GoogleServiceWorker("login")
            self.login_worker.log.connect(self._logger)
            self.login_worker.recordsDone.connect(self._activate_startup)
            self.login_worker.start()
        else:
            self._activate_startup()

    def _activate_startup(self, arg=None):
        self.worker = GoogleServiceWorker("get_sheets")
        self.worker.log.connect(self._logger)
        self.worker.recordsDone.connect(self._init_topics)
        self.worker.start()

    def _handle_search(self):
        query = self._view.get_search_text()

        if query:
            self._view.start_spinner()
            print(self._view.get_checked_topics())
            self.worker = GoogleServiceWorker("search", (query, self._view.get_checked_topics()))
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
        self.sheets = sheets
        
    def _init_topics(self, sheets):
        self._sheets = sheets
        self._view.add_topic_checkboxes(sheets)
        self._view.populate_topic_dropdowns(sheets)
        self._view.stop_spinner()

    def _handle_add_record(self):
        sheet = self._view.get_topic_text()
        category = self._view.get_category_text()
        title = self._view.get_title_text()

        # clear the category & title fields
        self._view.clear_fields()
        self._view.start_spinner()

        self.worker = GoogleServiceWorker("create_doc", (sheet, category, title))
        self.worker.log.connect(self._logger)
        self.worker.recordsDone.connect(self._add_rows)
        self.worker.start()
        


    def _connectSignals(self):
        self._view.search_button.clicked.connect(self._handle_search)
        self._view.add_record.clicked.connect(self._handle_add_record)

    def _logger(self, msg):
        self._view.set_log_message(msg)
