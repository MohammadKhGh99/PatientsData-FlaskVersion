import os
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import sqlite3
# import pandas as pd
import csv
from flask import flash

gauth = None
root_folder = None
drive = None
db_path = r"Patient.db"
excel_path = r"نسخ_إحتياطي.csv"


def do_backup_xlsx():
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Patient")
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]

            # Check if the file exists
            if os.path.exists(excel_path):
                # Remove the file
                os.remove(excel_path)

            # Write data to CSV file
            with open(excel_path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(column_names)  # Write column headers
                writer.writerows(rows)  # Write data rows



            # df = pd.read_sql("SELECT * from Patient", connection)
            # # Check if the file exists
            # if os.path.exists("نسخ_إحتياطي.xlsx"):
            #     # Remove the file
            #     os.remove("نسخ_إحتياطي.xlsx")
            # df.to_excel("نسخ_إحتياطي.xlsx")
        flash("تم التحويل بنجاح!", "success")
        return 0
    except Exception as e:
        flash("لم يتم التحويل إلى ملف إكسل! \n" + str(e), "error")
        print(e)
        return 1


def authentication_func():
    # Below code does the authentication
    # part of the code
    global gauth, root_folder, drive
    gauth = GoogleAuth()
    
    if os.path.exists('credentials.txt'):
        gauth.LoadCredentialsFile('credentials.txt')

         # Refresh the token if expired
        if gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()  # Reauthorize if needed

    else:
        # Perform OAuth authentication
        gauth.LocalWebserverAuth()  # Open a local webserver for user login

        # Save the credentials for future use
        gauth.SaveCredentialsFile('credentials.txt')
        
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


def save_func():
    do_backup_xlsx()
    global root_folder
    try:
        if drive is None or gauth is None:
            authentication_func()

        root_list = drive.ListFile({'q': f"'{root_folder['id']}' in parents and trashed=false"}).GetList() # type: ignore
        for file in root_list:
            if file['title'] == excel_path:
                file.Delete()
            if file['title'] == db_path:
                file.Delete()
        # iterating thought all the files/folder
        # of the desired directory

        for x in [db_path, excel_path]:
            f = drive.CreateFile({'parents': [{'id': f"{root_folder['id']}"}]}) # type: ignore
            f.SetContentFile(x)
            f.Upload()

            # Due to a known bug in pydrive if we
            # don't empty the variable used to
            # upload the files to Google Drive the
            # file stays open in memory and causes a
            # memory leak, therefore preventing its
            # deletion
            f = None
        flash("تم الحفظ في جوجل درايف!", "success")
        return 0
    except Exception as e:
        flash("لم يتم الحفظ! \n" + str(e), "error")
        print(e)
        return 1


def load_func():
    global root_folder
    try:
        if drive is None or gauth is None:
            authentication_func()

        root_list = drive.ListFile({'q': f"'{root_folder['id']}' in parents and trashed=false"}).GetList() # type: ignore
        for file in root_list:
            file.GetContentFile(fr"نسخ_إحتياطي\{file['title']}")
        flash("تم إستعادة الملفات بنجاح!", "success")
        return 0
    except Exception as e:
        flash("لم تتم الإستعادة! \n" + str(e), "error")
        print(e)
        return 1
