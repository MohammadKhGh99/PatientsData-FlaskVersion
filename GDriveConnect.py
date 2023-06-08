from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import tkinter.messagebox
import sqlite3
import pandas as pd

from flask import flash
gauth = None
root_folder = None
drive = None


def do_backup_xlsx():
    try:
        with sqlite3.connect("Patient.db") as connection:
            df = pd.read_sql("SELECT * from Patient", connection)
            df.to_excel("نسخ_إحتياطي.xlsx")
        return 0
    except Exception as e:
        return 1


def authentication_func():
    # Below code does the authentication
    # part of the code
    global gauth, root_folder, drive
    gauth = GoogleAuth()

    # Creates local webserver and auto
    # handles authentication.
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # searching for the root folder to save to
    file_name = "المعالجة بالرقية الشرعية"
    query = f"title = '{file_name}'"
    root_list_check = drive.ListFile({'q': query}).GetList()

    # Check if the file exists
    if root_list_check:
        root_folder = root_list_check[0]
    else:
        body = {'title': "المعالجة بالرقية الشرعية", 'mimeType': "application/vnd.google-apps.folder"}
        root_folder = drive.CreateFile(body)
        root_folder.Upload()


# replace the value of this variable
# with the absolute path of the directory
db_path = r"Patient.db"
xlsx_path = r"نسخ_إحتياطي.xlsx"


def save_func():
    do_backup_xlsx()
    global root_folder
    try:
        if drive is None or gauth is None:
            authentication_func()

        root_list = drive.ListFile({'q': f"'{root_folder['id']}' in parents and trashed=false"}).GetList()
        for file in root_list:
            if file['title'] == xlsx_path:
                file.Delete()
            if file['title'] == db_path:
                file.Delete()
        # iterating thought all the files/folder
        # of the desired directory

        for x in [db_path, xlsx_path]:
            f = drive.CreateFile({'parents': [{'id': f"{root_folder['id']}"}]})
            f.SetContentFile(x)
            f.Upload()

            # Due to a known bug in pydrive if we
            # don't empty the variable used to
            # upload the files to Google Drive the
            # file stays open in memory and causes a
            # memory leak, therefore preventing its
            # deletion
            f = None
        return 0
    except Exception as e:
        print(str(e))
        return 1


def load_func():
    try:
        if drive is None or gauth is None:
            authentication_func()

        root_list = drive.ListFile({'q': f"'{root_folder['id']}' in parents and trashed=false"}).GetList()
        for file in root_list:
            file.GetContentFile(fr"نسخ_إحتياطي\{file['title']}")

        # with sqlite3.connect("Patient.db") as connection:
        #     cursor = connection.cursor()
        #     cursor.execute('DELETE FROM Patient')
        #     connection.commit()

            # wb = pd.read_excel('BackUp.xlsx', sheet_name='Sheet')
            # wb.to_sql(name='Patient', con=connection, if_exists='replace', index=True)
            # connection.commit()
        return 0
    except Exception as e:
        return 1
