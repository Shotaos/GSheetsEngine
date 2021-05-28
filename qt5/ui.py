from qt5.spin import QtWaitingSpinner
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QMainWindow, QTableWidgetItem, QLabel, QHeaderView
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QLabel, QMessageBox
import os


class SheetsEngineUI(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join('qt5', 'gui_elements', 'mainUI.ui'), self)
        self.show()
        self.search_line_input.returnPressed.connect(self.search_button.click)
        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def start_spinner(self):
        self.spinner.start()

    def stop_spinner(self):
        self.spinner.stop()

    def add_table_columns(self, columns):
        self.main_table.setColumnCount(len(columns))
        self.main_table.setHorizontalHeaderLabels(columns)

    def addRow(self, row_values, link):
        rowCount = self.main_table.rowCount()
        columnCount = self.main_table.columnCount()
        self.main_table.insertRow(rowCount)

        # Insert first column
        q = QLabel(self)
        q.setOpenExternalLinks(True)
        q.setText('<a href="{}">{}</a>'.format(link, row_values[0]))
        self.main_table.setCellWidget(rowCount, 0, q)

        for col in range(1, columnCount):
            i = QTableWidgetItem(str(row_values[col]))
            self.main_table.setItem(rowCount, col, i)

    def resize_table(self):
        self.main_table.resizeColumnsToContents()

    def get_column_by_header(self, header):
        num_of_columns = self.main_table.columnCount()
        for col in range(num_of_columns):
            col_name = self.main_table.horizontalHeaderItem(col).text()
            if header == col_name:
                return col
        return None

    def get_topic_text(self):
        return self.add_topic_dropdown.currentText()

    def get_category_text(self):
        return self.category_line.text()

    def get_title_text(self):
        return self.title_line.text()

    def clear_table(self):
        self.main_table.setColumnCount(0)
        self.main_table.setRowCount(0)

    def populate_topic_dropdowns(self, topics):
        self.add_topic_dropdown.addItems(topics)
        # self.search_topic_dropdown.addItems(topics)

    def get_search_text(self):
        return self.search_line_input.text()

    def add_topic_checkboxes(self, topics):
        self.topic_checkboxes = []
        for topic in topics:
            cb = QCheckBox(topic.capitalize())
            self.horizontalLayout_5.addWidget(cb)
            self.topic_checkboxes.append(cb)

    def get_checked_topics(self):
        topics_chosen = []
        for cb in self.topic_checkboxes:
            if cb.isChecked():
                topics_chosen.append(cb.text())
        return topics_chosen


def alert_dialog():
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    message = """
    <p align='center'>Authentication is required.
    Default browser will open after you press the OK Button. Please authenticate with your Google account.</p>
    """
    msgBox.setText(message)
    msgBox.setWindowTitle("Login required")
    msgBox.setStandardButtons(QMessageBox.Ok)

    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Ok:
        print('OK')
