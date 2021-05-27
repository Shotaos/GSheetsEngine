class SheetsController():

    def __init__(self, model, view):
        self._model = model
        self._view = view

        # Connect signals and slots
        self._connectSignals()

    def _connectSignals(self):
        pass

