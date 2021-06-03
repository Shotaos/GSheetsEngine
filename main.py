import sys

from PyQt5.QtWidgets import QApplication
from qt5.controller import SheetsController
from qt5.ui import SheetsEngineUI, SettingsUI
def main():
    # Create an instance of `QApplication`
    sheetsApp = QApplication(sys.argv)
    view = SheetsEngineUI()
    settings = SettingsUI(view)
    controller = SheetsController(view, settings)
    sys.exit(sheetsApp.exec_())


# if __name__ == "__main__":
#     main()
