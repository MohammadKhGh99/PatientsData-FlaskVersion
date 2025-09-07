from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import shutil
import smtplib
import sqlite3

from dotenv import load_dotenv
from Constants import *

from flask import flash, redirect, request

project_folder = os.path.expanduser(os.path.abspath(os.path.curdir))  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

GMAIL_PASS = os.getenv("GMAIL_PASS")
MY_GMAIL = os.getenv("MY_GMAIL")

def save_patient_func(form, update=False):
    # fullname = form['fullname'].strip()
    firstname = form['firstname'].strip()
    middlename = form['middlename'].strip()
    lastname = form['lastname'].strip()
    id_number = form['id'].strip()
    year_num = form['year'].strip()
    print(year_num)
    serial_num = form['serialNum'].strip()
    status = form['status'].strip()
    age = form['age'].strip()
    gender = form['gender'].strip()
    children = form['children'].strip()
    prayer = form['prayer'].strip()
    city = form['city'].strip()
    phone = form['phone'].strip()
    work = form['work'].strip()
    health = form['health'].strip()
    companion = form['companion'].strip()
    description = form['description'].strip()
    diagnosis = form['diagnosis'].strip()
    therapy = form['therapy'].strip()
    
    with sqlite3.connect("علاج.db") as connection:
        cursor = connection.cursor()
        # condition of updating a patient
        # splitted_name = fullname.split(' ')
        # if len(splitted_name) == 3:
        #     first, middle, last = splitted_name
        # else:
        #     first, last = splitted_name
        #     middle = ""
        fullname = f"{firstname} {middlename} {lastname}"
        if update:
            try:
                cursor.execute(f"update Patient "
                            #    f"set الرقم_التسلسلي = '{serial_num}',"
                               f"set السنة = '{year_num}',"
                               f"الإسم_الثلاثي = '{fullname}',"
                               f"الإسم_الشخصي = '{firstname}',"
                               f" إسم_الأب = '{middlename}',"
                               f" إسم_العائلة = '{lastname}', "
                               f"رقم_الهوية = '{id_number}',"
                               f" الجنس = '{gender}', "
                               f"الحالة_الإجتماعية = '{status}',"
                               f" العمر = '{age}', "
                               f"أولاد = '{children}',"
                               f" صلاة = '{prayer}', "
                               f"صحة = '{health}',"
                               f" العمل = '{work}', "
                               f"المرافق = '{companion}',"
                               f" البلد = '{city}', "
                               f"الهاتف = '{phone}',"
                               f" وصف_الحالة = '{description}', "
                               f"التشخيص = '{diagnosis}',"
                               f" العلاج = '{therapy}' "
                               f"where الرقم_التسلسلي = '{serial_num}'") # and الإسم_الثلاثي ='{fullname}'")
                connection.commit()
                flash('تم الحفظ بنجاح!', 'success')
            except Exception as e:
                connection.rollback()
                flash('حدث خطأ أثناء الحفظ! \n' + str(e), 'error')
                print(e)
                raise e
        # condition of adding a new patient
        else:
            try:
                cursor.execute(
                    "INSERT INTO Patient "
                    "(السنة, الإسم_الثلاثي, الإسم_الشخصي, إسم_الأب, إسم_العائلة, "
                    "رقم_الهوية, الجنس, الحالة_الإجتماعية, العمر, أولاد, صلاة, صحة, "
                    "العمل, المرافق, البلد, الهاتف, وصف_الحالة, التشخيص, العلاج) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (year_num, fullname, firstname, middlename, lastname,
                    id_number, gender, status, age, children, prayer, health,
                    work, companion, city, phone, description, diagnosis, therapy))
                connection.commit()
                flash('تم الحفظ بنجاح!', 'success')
            except Exception as e:
                connection.rollback()
                flash('حدث خطأ أثناء الحفظ! \n' + str(e), 'error')
                print(e)
                raise e
    if update:
        return True, (firstname, middlename, lastname, id_number, serial_num, year_num, status, age, gender, children, prayer, city, phone, work, health, companion, description, diagnosis, therapy)
    return True


def search_patient_func(search_method, search=None, search1=None):
    to_return = []
    with sqlite3.connect("علاج.db") as connection:
        cursor = connection.cursor()

        wanted_cols = f"الرقم_التسلسلي, السنة, الإسم_الثلاثي, الإسم_الشخصي, إسم_الأب, إسم_العائلة, رقم_الهوية, الجنس, الحالة_الإجتماعية, العمر, أولاد, صلاة, صحة, العمل, المرافق, البلد, الهاتف, وصف_الحالة, التشخيص, العلاج"

        try:
            # taking all the patients
            if search is None or search.strip() == "":
                cursor.execute(f"select {wanted_cols} from Patient")
                data = cursor.fetchall()
                connection.commit()
                for j in range(len(data)):
                    row = {ALL_DATA[i]: data[j][i] for i in range(len(ALL_DATA))}
                    to_return.append(row)
            else:
                if search_method == ID_SEARCH:
                    cursor.execute(
                        f"select {wanted_cols} from Patient where cast(رقم_الهوية as varchar(9)) = '{search}'")
                else:
                    if search_method == ALL_NAME:
                        cursor.execute(f"select {wanted_cols} from Patient where الإسم_الثلاثي = '{search}'")
                    elif search_method == FLNAME:
                        cur = search.split(" ")
                        cursor.execute(
                            f"select {wanted_cols} from Patient where الإسم_الشخصي = '{search}' and إسم_العائلة = '{search1}'")
                    elif search_method == FMNAME:
                        cur = search.split(" ")
                        cursor.execute(
                            f"select {wanted_cols} from Patient where الإسم_الشخصي = '{search}' and إسم_الأب = '{search1}'")
                    elif search_method == FNAME:
                        cursor.execute(f"select {wanted_cols} from Patient where الإسم_الشخصي = '{search}'")
                    elif search_method == LNAME:
                        cursor.execute(f"select {wanted_cols} from Patient where إسم_العائلة = '{search}'")
                data = cursor.fetchall()
                connection.commit()
                for j in range(len(data)):
                    row = {ALL_DATA[i]: data[j][i] for i in range(len(ALL_DATA))}
                    to_return.append(row)
        except Exception as e:
            connection.rollback()
            flash('حدث خطأ أثناء البحث! \n' + str(e), 'error')
            print(e)
            return -1, "ERROR in SQL!"

        if len(to_return) == 0:
            if search_method == ID_SEARCH:
                return -1, ID_NOT_EXISTS
            else:
                return -1, NAME_NOT_EXISTS

    return 0, to_return


def update_last_backup_time_in_file(source):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("last_backup_time.txt", "w", encoding="utf-8-sig") as file:
        file.write(now + source)

def get_last_backup_time_from_file():
    try:
        with open("last_backup_time.txt", "r", encoding="utf-8-sig") as file:
            data = file.read()
            return data
    except FileNotFoundError:
        return "-"
    


def send_email(sender, app_password, to, subject, message_text, msg_type, attachment=None):

    # Create a secure connection to the Gmail SMTP server
    # with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)

    smtp_server.starttls()

    # Log in to your Gmail account using the App Password
    smtp_server.login(sender, app_password)
    
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(message_text, msg_type))

    # If there's an attachment, add it to the email
    if attachment:
        with open(attachment, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(f.name)}'
            )
            msg.attach(part)

    # send email
    smtp_server.send_message(msg)

    smtp_server.quit()

def do_backup_email(email):
    try:
        now = datetime.now()
        backup_filename = f"patients_backup_{now.strftime('%Y%m%d_%H%M%S')}.db"

        # Copy the database file
        shutil.copy2("علاج.db", backup_filename)

        send_email(MY_GMAIL, 
                GMAIL_PASS,
                email,
                "نسخة احتياطية من قاعدة البيانات",
                f"تم أخذ نسخة احتياطية من قاعدة البيانات في {now.strftime('%Y-%m-%d %H:%M:%S')}\n",
                "plain",
                backup_filename)
        
        # Update the last backup time in the JSON file
        update_last_backup_time_in_file(" عبر الإيميل")

        # print(f"Backup created: {backup_filename}")
        os.remove(backup_filename)
        flash("تم أخذ نسخة احتياطية من قاعدة البيانات بنجاح", "success")
    except Exception as e:
        flash("حدث خطأ أثناء أخذ النسخة الاحتياطية! \n" + str(e), "error")
        # print(e)
    return redirect(request.referrer)


def create_table():
    arabic_sql_create_table = """
    create table if not exists Patient(
        الرقم_التسلسلي INTEGER PRIMARY KEY AUTOINCREMENT,
        السنة nvarchar(4),
        الإسم_الثلاثي nvarchar(45),
        الإسم_الشخصي nvarchar(15),
        إسم_الأب nvarchar(15),
        إسم_العائلة nvarchar(15),
        رقم_الهوية nvarchar(9),
        الجنس nvarchar(7),
        الحالة_الإجتماعية nvarchar(15),
        العمر nvarchar(3),
        أولاد nvarchar(3),
        صلاة nvarchar(5),
        صحة nvarchar(30),
        العمل nvarchar(30),
        المرافق nvarchar(30),
        البلد nvarchar(20),
        الهاتف nvarchar(12),
        وصف_الحالة nvarchar(500),
        التشخيص nvarchar(500),
        العلاج nvarchar(500)
    )
    """

    with sqlite3.connect("علاج.db") as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(arabic_sql_create_table)
            connection.commit()
            # # Reset the auto-increment sequence to start from 1
            cursor.execute("INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES ('Patient', 1)")

            # cursor.execute("DELETE FROM sqlite_sequence WHERE name='Patient'")
            connection.commit()
        except Exception as e:
            flash(str(e), 'error')
            connection.rollback()
            print(e)


def drop_table():
    """Reset the auto-increment sequence to start from 1"""
    with sqlite3.connect("علاج.db") as connection:
        cursor = connection.cursor()
        try:
            # Reset the auto-increment sequence
            # cursor.execute("DELETE FROM sqlite_sequence WHERE name='Patient'")
            cursor.execute("DROP TABLE Patient")
            connection.commit()
            print("table Patient dropped successfully.")
        except Exception as e:
            connection.rollback()
            print(f"Error dropping table Patient: {e}")
