import os
import sys
from qt5.spin import QtWaitingSpinner
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QMainWindow, QTableWidgetItem, QLabel, QHeaderView
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QLabel, QMessageBox, QDialog


class SettingsUI(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(os.path.join('qt5',
                                'gui_elements', 'settUI.ui'), self)

    def _add_topic_checkboxes(self, topics, excluded):
        self.sheets = []
        positions = [(i, j) for i in range(len(topics)) for j in range(4)]
        for i, topic in enumerate(topics):
            cb = QCheckBox(topic.capitalize())
            cb.setChecked(topic in excluded)
            self.exclude_sheets.addWidget(cb, *positions[i])
            self.sheets.append(cb)

    def set_settings(self, settings, sheets):
        self.sheetId.setText(settings['sheetId'])
        self._add_topic_checkboxes(sheets, settings['excludeSheets'])

    def get_settings(self):
        topics_excluded = []
        for cb in self.sheets:
            if cb.isChecked():
                topics_excluded.append(cb.text())
        return {'sheetId': self.sheetId.text(), 'excludeSheets': topics_excluded}


class SheetsEngineUI(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join('qt5',
                                'gui_elements', 'mainUI.ui'), self)
        self.show()
        self.search_line_input.returnPressed.connect(self.search_button.click)
        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def start_spinner(self):
        self.spinner.start()

    def stop_spinner(self):
        self.spinner.stop()

    def set_log_message(self, message):
        self.log_text.setText(message)

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

    def clear_table(self):
        self.main_table.setRowCount(0)

    def clear_fields(self):
        self.category_line.setText("")
        self.title_line.setText("")
        self.search_line_input.setText("")

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

    def populate_topic_dropdowns(self, topics):
        self.add_topic_dropdown.clear()
        self.add_topic_dropdown.addItems(topics)
        # self.search_topic_dropdown.addItems(topics)

    def get_search_text(self):
        return self.search_line_input.text()

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            widgetToRemove = layout.itemAt(i).widget()
            # remove it from the layout list
            layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

    def add_topic_checkboxes(self, topics):
        self.topic_checkboxes = []
        self.clear_layout(self.horizontalLayout_5)
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
    <p align='center'>Authentication is required.</p>
    """
    msgBox.setText(message)
    msgBox.setWindowTitle("Login required")
    msgBox.setStandardButtons(QMessageBox.Ok)

    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Ok:
        print('OK')
