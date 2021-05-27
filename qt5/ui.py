import os
from PyQt5 import QtGui

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QLabel
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt
from PyQt5 import uic

        
class SheetsEngineUI(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join('qt5', 'gui_elements', 'mainUI.ui'), self)
        self.show()
    
    def add_table_columns(self, columns):
        self.main_table.setColumnCount(len(columns))
        self.main_table.setHorizontalHeaderLabels(columns)

    def addRow(self, row_values):
        rowCount = self.main_table.rowCount()
        columnCount = self.main_table.columnCount()
        self.main_table.insertRow(rowCount)
        q = QLabel(self)
        for col in range(columnCount):
            i = QTableWidgetItem(str(row_values[col]))
            if col == 0:
                i.setForeground(QBrush(QColor(0,0,127), Qt.BrushStyle.SolidPattern))
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
        #self.search_topic_dropdown.addItems(topics)

    def get_search_text(self):
        return self.search_line_input.text()
