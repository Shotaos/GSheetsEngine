import sys

from PyQt5.QtWidgets import QApplication

from qt5.ui import SheetsEngineUI, SettingsUI
from qt5.controller import SheetsController

__version__ = '1.0'
__author__ = 'irakli'


def main():
    # Create an instance of `QApplication`
    sheetsApp = QApplication(sys.argv)
    view = SheetsEngineUI()
    settings = SettingsUI(view)
    controller = SheetsController(view, settings)
    sys.exit(sheetsApp.exec_())


if __name__ == "__main__":
    main()
