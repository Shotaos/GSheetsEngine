import sys

from PyQt5.QtWidgets import QApplication

from qt5.ui import SheetsEngineUI
from qt5.model import SheetsModel
from qt5.controller import SheetsController

__version__ = '1.0'
__author__ = 'irakli'


def main():
    # Create an instance of `QApplication`
    sheetsApp = QApplication(sys.argv)
    view = SheetsEngineUI()
    model = SheetsModel
    controller = SheetsController(model, view)
    sys.exit(sheetsApp.exec_())


if __name__ == "__main__":
    main()
