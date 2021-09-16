from PyQt5.QtCore import QThread, pyqtSignal
from googleapiclient import errors
from sheets import GoogleSheets
import socket
import webbrowser
import httplib2


class GoogleServiceWorker(QThread):

        log = pyqtSignal(str)
        recordsDone = pyqtSignal(list)

        def __init__(self, sheetId, command, args=None, parent=None):
                super(GoogleServiceWorker, self).__init__(parent)
                self.command = command
                self.args = args
                self.sheetId = sheetId

        def run(self):
                if self.command not in ["login", "get_sheets", "search", "insert_row", "create_doc","open_sheet"]:
                        self.log.emit("Wrong command passed to GoogleServiceWorker")
                        self.recordsDone.emit([])
                        return
                try:
                        google = GoogleSheets(self.sheetId)

                        if self.command == "login":
                                google.login()
                                self.log.emit("Successful Login")
                                self.recordsDone.emit([])
                        if self.command == "get_sheets":
                                sheets = google.get_sheet_names()
                                self.log.emit("Retrived {} sheets successfully".format(len(sheets)))
                                self.recordsDone.emit(sheets)
                        elif self.command == "search":
                                result = google.search(*self.args)
                                self.log.emit("Query: '{}'      Found {} results.".format(self.args[0], len(result)))
                                self.recordsDone.emit(result)
                        elif self.command == "insert_row":
                                pass
                        elif self.command == "create_doc":
                                data = self.args
                                doc_url, code_url = google.create_documents(data)
                                self.log.emit("Google Docs: '{}' successfully created.".format(data['title']))
                                webbrowser.open(doc_url, new=2)
                                row = [data['category'], data['title'], doc_url, code_url]
                                google.insert_row(data['sheet'], row)
                                self.recordsDone.emit([[data['sheet']] + row])
                        elif self.command == "open_sheet":
                                webbrowser.open("https://docs.google.com/spreadsheets/d/" + self.sheetId + "/edit", new=2)
                except errors.HttpError as e:
                        self.log.emit("Http error: Most likely sheetID is invalid.  " + str(e)[:40]+ '...')
                        self.recordsDone.emit([])

                except (errors.Error, socket.error, httplib2.ServerNotFoundError) as e:
                        self.log.emit(str(e))
                        self.recordsDone.emit([])
