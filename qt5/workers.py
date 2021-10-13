from PyQt5.QtCore import QThread, pyqtSignal
from googleapiclient import errors
from gsuite import NotesService, UnrealService
from config import ICONS_CACHE, ASSETS_CACHE
import socket
import tempfile
import pathlib
import json
import glob
import shutil
import zipfile
import os
import urllib
import queue
import webbrowser
import httplib2


class ScanProjectsWorker(QThread):
        exclude = [
                'C://windows',
                'C://windows',
        ]
                

        newProject = pyqtSignal(tuple)
        statistics = pyqtSignal(tuple)
        done = pyqtSignal(bool)

        def run(self):
            total_dirs = 0
            index = 0
            drives = []

            if os.name == 'nt':
                possible_drives = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                drives = drives + [f"{_}://" for _ in possible_drives if os.path.exists(f"{_}:")]
                print("Windows drives found:", ",".join(drives))
            elif os.name =='posix':
                drives.append('/')

            for drive in drives:

                for root, dirs, files in os.walk(drive, topdown=True):
                    dirs[:] = [d for d in dirs if d not in ScanProjectsWorker.exclude]
                    index += 1

                    if index % 20 == 0:
                        self.statistics.emit((index, total_dirs, root))

                    # Look for .uproject file in current directory
                    for _file in files:
                        if _file.endswith('.uproject'):
                            total_dirs += 1
                            # Parse .uproject to get the project name
                            try:
                                with open(os.path.join(root, _file)) as f:
                                    uproject = json.load(f)
                                    # Make assumption that first module name is the project name
                                    name = uproject["Modules"][0]["Name"]
                                    self.newProject.emit((name, root))

                            except (json.JSONDecodeError, KeyError, IndexError):
                                pass
            self.done.emit(True)

            

class AssetThumbnailWorker(QThread):
        resultReady = pyqtSignal(tuple)

        def __init__(self, queue, parent=None):
            super().__init__(parent)
            self.queue = queue

        def run(self):
            while not self.queue.empty():
                try:
                    index, _id = self.queue.get(block=False)
                    filename = os.path.join(ICONS_CACHE, _id)

                    if not os.path.isfile(filename):
                        unreal = UnrealService(None)
                        unreal.drive_download_file_cache(_id, ICONS_CACHE)
                    self.resultReady.emit((index, open(filename, 'br').read()))

                except (queue.Empty, urllib.error.HTTPError, urllib.error.URLError) as e:
                    print(e)

class AssetsDownloaderWorker(QThread):
        done = pyqtSignal(list)
        log = pyqtSignal(str)

        def __init__(self, data, parent=None):
            super().__init__(parent)
            self.data = data

        def run(self):
            try:
                _id, overwrite, data = self.data
                filename = os.path.join(ASSETS_CACHE, _id)

                if not os.path.isfile(filename):
                    unreal = UnrealService(None)
                    unreal.drive_download_file_cache(_id, ASSETS_CACHE)

                with tempfile.TemporaryDirectory() as tmpdir:
                    tmpdir = pathlib.Path(tmpdir)

                    if zipfile.is_zipfile(filename):
                        shutil.unpack_archive(filename, tmpdir, 'zip')
                    else:
                        shutil.copy(filename, tmpdir)

                    for target_dir in [pathlib.Path(_) for _ in data]:
                        for _file in tmpdir.glob('*'):
                            source = tmpdir / _file.name
                            target = target_dir / _file.name

                            print(source, target)
                            if overwrite or not target.exists():
                                if source.is_dir():
                                    shutil.copytree(source, target, dirs_exist_ok=True)
                                elif source.is_file():
                                    shutil.copy(source, target)

                    self.log.emit("Successfully Added Asset")
            except Exception as e:
                print(e)
                self.log.emit(f"Asset Failed {e}")
            finally:
                self.done.emit([])

            
            

class GoogleServiceWorker(QThread):

        log = pyqtSignal(str)
        recordsDone = pyqtSignal(list)
        codeDone = pyqtSignal(str)

        def __init__(self, sheetId, command, args=None, assets_sheetId=None, parent=None):
            super(GoogleServiceWorker, self).__init__(parent)
            self.command = command
            self.args = args
            self.assets_sheetId = assets_sheetId
            self.sheetId = sheetId
            self.notes_service = NotesService(sheetId)

        def run(self):
            try:
                notes = NotesService(self.sheetId)
                unreal = UnrealService(self.assets_sheetId)

                if self.command == "search_assets":
                    result = unreal.search(*self.args)
                    self.log.emit("Query: '{}'      Found {} results.".format(self.args[0], len(result)))
                    self.recordsDone.emit(result)
                elif self.command == "login":
                    notes.authenticate()
                    unreal.authenticate()
                    self.log.emit("Successful Login")
                    self.recordsDone.emit([])
                elif self.command == "get_sheets":
                    sheets = notes.get_sheet_names()
                    self.log.emit("Retrived {} sheets successfully".format(len(sheets)))
                    self.recordsDone.emit(sheets)
                elif self.command == "search":
                    result = notes.search(*self.args)
                    self.log.emit("Query: '{}'      Found {} results.".format(self.args[0], len(result)))
                    self.recordsDone.emit(result)
                elif self.command == "upload_asset":
                    data, settings = self.args
                    try:
                        asset_id = unreal.upload_zipped_folder(data['path'], settings['assetsDriveDirId'])
                        thumbnail_id = '' if not data['icon'] else unreal.drive_upload_file(
                                settings['assetsDriveDirId'], data['icon'])['id']

                        row = ['Asset', data['ue_version'], data['name'], data['tags'], thumbnail_id, asset_id]
                        unreal.insert_row(
                                'assets',
                                row,
                                'A:F')

                        self.log.emit("Asset uploaded successfully")
                    except (TimeoutError, Exception) as e:
                        self.log.emit(f"Asset upload Failed {e}")
                    finally:
                        self.recordsDone.emit([])

                elif self.command == "upload_regular":
                    data, settings = self.args
                    try:
                        file_id = unreal.upload_zipped_folder(data['path'], settings['assetsDriveDirId'])
                        thumbnail_id = '' if not data['icon'] else unreal.drive_upload_file(
                                settings['assetsDriveDirId'], data['icon'])['id']

                        row = [data['type'], '', data['name'], data['tags'], thumbnail_id, file_id]
                        unreal.insert_row(
                                'assets',
                                row,
                                'A:F')

                        self.log.emit("Asset uploaded successfully")
                    except (TimeoutError, Exception) as e:
                        self.log.emit(f"Asset upload Failed {e}")
                    finally:
                        self.recordsDone.emit([])

                elif self.command == "get_copy":
                    code = None
                    try:
                        code = notes.get_document_text(self.args)
                        if code:
                            self.log.emit("Code copied successfully")
                        else:
                            self.log.emit("Error copying code, check the code document")
                    except Exception as e:
                        self.log.emit("Error copying code: " + str(e))
                    self.codeDone.emit(code)


                elif self.command == "create_doc":
                    data = self.args
                    doc_url, code_url = notes.create_documents(data)
                    self.log.emit("Google Docs: '{}' successfully created.".format(data['title']))
                    webbrowser.open(doc_url, new=2)
                    row = [data['category'], data['title'], doc_url, code_url]
                    notes.insert_row(data['sheet'], row)
                    self.recordsDone.emit([[data['sheet']] + row])
                elif self.command == "open_sheet":
                    webbrowser.open("https://docs.notes.com/spreadsheets/d/" + self.sheetId + "/edit", new=2)
                elif self.command == "refresh_cache":
                    self.log.emit("Updating Cache!")
                    notes.get_cache()
                    unreal.get_cache()
                    self.log.emit("Cache updated successfully!")
                    self.recordsDone.emit([])
                else:
                    self.log.emit("Wrong command passed to GoogleServiceWorker")
                    self.recordsDone.emit([])

            except errors.HttpError as e:
                    print(e)
                    self.log.emit("Http error: Most likely sheetID is invalid.  " + str(e)[:40]+ '...')
                    self.recordsDone.emit([])

            except (errors.Error, socket.error, httplib2.ServerNotFoundError) as e:
                    self.log.emit(str(e))
                    self.recordsDone.emit([])
