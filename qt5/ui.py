import os
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
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
       
        for col in range(columnCount):
            self.main_table.setItem(rowCount, col, QTableWidgetItem(str(row_values[col])))

    def resize_table(self):
        self.main_table.resizeColumnsToContents()

    def get_column_by_header(self, header):
        num_of_columns = self.main_table.columnCount()
        for col in range(num_of_columns):
            col_name = self.main_table.horizontalHeaderItem(col).text()
            if header == col_name:
                return col
        return None

    def clear_table(self):
        self.main_table.setColumnCount(0)
        self.main_table.setRowCount(0)

    def populate_topic_dropdowns(self, topics):
        self.add_topic_dropdown.addItems(topics)
        self.search_topic_dropdown.addItems(topics)

