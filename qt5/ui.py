import os
import webbrowser
import queue
from qt5.workers import AssetThumbnailWorker
from qt5.spin import QtWaitingSpinner
from PyQt5 import QtGui, uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWidgets import QCheckBox, QMainWindow, QTableWidgetItem, QLabel, QHeaderView, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QLabel, QMessageBox, QDialog, QPushButton, QSpacerItem, QApplication

class AddRecordUI(QDialog):
    def __init__(self, sheets=["1","2"]):
        super().__init__()
        uic.loadUi(os.path.join('qt5', 'gui_elements', 'addUIVertical.ui'), self)
        self.setWindowIcon(QtGui.QIcon(os.path.join('assets', 'icon.ico')))
        for sheet in sheets:
            self.topic.addItem(sheet)

    def get_data(self):
        return {
            "title": self.title.text(),
            "sheet": self.topic.itemData(self.topic.currentIndex(), 2),
            "category": self.category.text(),
            "code": self.code.toPlainText(),
            "youtube": self.youtube.text(),
            "quick_text": self.quick_text.toPlainText(),
        }


class AssetResults(QDialog):
    def __init__(self, assets, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join('qt5', 'gui_elements', 'assetResultsDialog.ui'), self)
        self.assets = assets
        self.widgets = []
        self.threads = []
        q = queue.Queue()

        layout = self.results_layout.layout()

        for k, thumbnail in enumerate(assets):
            asset = AssetResultWidget()
            self.widgets.append(asset)
            q.put((k, thumbnail))
            layout.addWidget(asset, k // 4, k % 4)

        for i in range(10):
            thread = AssetThumbnailWorker(q)
            thread.resultReady.connect(self.updateThumbnail)
            thread.start()
            self.threads.append(thread)


    def updateThumbnail(self, _data):
        index, data = _data
        image = QtGui.QImage()
        image.loadFromData(data)
        self.widgets[index].thumbnail.setPixmap(QtGui.QPixmap(image).scaled(100, 100, Qt.KeepAspectRatio))

class AssetResultWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join('qt5', 'gui_elements', 'assetResultWidget.ui'), self)
        
class SettingsUI(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(os.path.join('qt5', 'gui_elements', 'settUI.ui'), self)
        self.settings = {}

    def _add_topic_checkboxes(self, topics, excluded):
        self.sheets = []
        positions = [(i, j) for i in range(len(topics)) for j in range(4)]
        for i, topic in enumerate(topics):
            cb = QCheckBox(topic)
            cb.setChecked(topic in excluded)
            self.exclude_sheets.addWidget(cb, *positions[i])
            self.sheets.append(cb)

    def set_setting(self, key, value):
        self.settings[key] = value

    def set_settings(self, settings, sheets):
        self.sheetId.setText(settings['sheetId'])
        self._add_topic_checkboxes(sheets, settings['excludeSheets'])

    def get_settings(self):
        topics_excluded = []
        for cb in self.sheets:
            if cb.isChecked():
                topics_excluded.append(cb.text())
        return {'sheetId': self.sheetId.text(), 'excludeSheets': topics_excluded, **self.settings}


class SheetsEngineUI(QMainWindow):

    copy = pyqtSignal(str)
    filtersChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join('qt5', 'gui_elements', 'mainUI.ui'), self)
        self.setWindowIcon(QtGui.QIcon(os.path.join('assets', 'icon.ico')))
        self.show()
        self.search_line_input.returnPressed.connect(self.search_button.click)
        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        #self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.filter_btns_layout.addStretch(1)

    def start_spinner(self):
        self.spinner.start()

    def stop_spinner(self):
        self.spinner.stop()

    def set_log_message(self, message):
        self.log_text.setText(message)

    def add_table_columns(self, columns):
        self.main_table.setColumnCount(len(columns))
        self.main_table.setHorizontalHeaderLabels(columns)
        self.main_table.horizontalHeader().setMinimumSectionSize(200)
        self.main_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.main_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def addRow(self, row_values, link):
        rowCount = self.main_table.rowCount()
        columnCount = self.main_table.columnCount()
        self.main_table.insertRow(rowCount)

        # Insert first column
        q = QLabel(self)
        q.setOpenExternalLinks(True)

        if link:
            q.setText('<a href="{}">{}</a>'.format(link, row_values[0]))
        else:
            q.setText(row_values[0])

        self.main_table.setCellWidget(rowCount, 0, q)

        i = QTableWidgetItem(str(row_values[1]))
        self.main_table.setItem(rowCount, 1, i)

        # If record has code docuemtn url
        if row_values[2]:
            layout = QHBoxLayout()
            copy = QPushButton('Copy')
            copy.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            copy.setStyleSheet('background-color:#585e5a; color:white')
            copy.clicked.connect(lambda x: self.copy.emit(row_values[2]))
            edit = QPushButton('Edit')
            edit.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            edit.clicked.connect(lambda x: webbrowser.open(row_values[2], new=2))
            layout.addStretch(1)
            layout.setContentsMargins(10, 0, 10, 0)
            layout.addWidget(copy)
            layout.addWidget(edit)

            container = QWidget(self.main_table)
            container.setLayout(layout)

            self.main_table.setCellWidget(rowCount, 2, container)

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
            if widgetToRemove:
                layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

    def add_topic_buttons(self, topics, active_topics):
        self.topic_checkboxes = []
        layout = self.filter_btns_layout
        self.clear_layout(layout)
        for topic in topics:
            cb = QPushButton(text=topic.capitalize())
            cb.clicked.connect(lambda : self.topic_button_clicked(cb))
            cb.setStyleSheet("min-width:150px")
            cb.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            cb.setCheckable(True)
            cb.setChecked(topic.lower() in active_topics)
            layout.insertWidget(layout.count() - 1, cb)
            self.topic_checkboxes.append(cb)
        


    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text, QtGui.QClipboard.Clipboard)
        if clipboard.supportsSelection():
            clipboard.setText(text, QtGui.QClipboard.Selection)

    def topic_button_clicked(self, button):
        self.filtersChanged.emit()

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
