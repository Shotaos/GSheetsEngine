import webbrowser
from sheets import GoogleSheets
from qt5.ui import alert_dialog

class SheetsController():
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self.gservice = GoogleSheets()

        if not self.gservice.check_credentials():
            alert_dialog()

        self._sheets = self.gservice.get_sheet_names()
        self._view.add_table_columns(['Title', 'Cateogry', 'Topic'])
        # Connect signals and slots
        self._init_topics()
        self._connectSignals()


    def _handle_search(self):
        query = self._view.get_search_text()
        if query:
            self._add_rows(self.gservice.search(query))

    def _add_rows(self, rows):
        if rows:
            for row in rows:
                topic, category, title, link = row
                self._view.addRow([title, category, topic], link)
        
    def _init_topics(self):
        self._view.populate_topic_dropdowns(self._sheets)

    def _handle_add_record(self):
        sheet = self._view.get_topic_text()
        category = self._view.get_category_text()
        title = self._view.get_title_text()
        url = self.gservice.create_doc(title)
        self.gservice.insert_row(sheet, (category, title, url))
        webbrowser.open(url, new=2)
        self._add_rows(self.gservice.search(title))

    def _connectSignals(self):
        self._view.search_button.clicked.connect(self._handle_search)
        self._view.add_record.clicked.connect(self._handle_add_record)

