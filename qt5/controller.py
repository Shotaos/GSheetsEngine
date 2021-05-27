from sheets import GoogleSheets

class SheetsController():
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self.gservice = GoogleSheets()
        self._sheets = self.gservice.get_sheet_names()
        self._view.add_table_columns(['Title', 'Cateogry', 'Topic'])
        # Connect signals and slots
        self._connectSignals()

    def _handle_search(self):
        query = self._view.get_search_text()
        # self._view.get_selected_filters()
        self._add_rows(self.gservice.search(query))

    def _add_rows(self, rows):
        if rows:
            for row in rows:
                topic, category, title, link = row
                self._view.addRow([title, category, topic])
        
    def _init_topics(self):
        pass

    def _connectSignals(self):
        self._view.search_button.clicked.connect(self._handle_search)

