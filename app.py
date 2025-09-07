from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import shutil
import signal
import smtplib
import sqlite3
from Constants import *
from GDriveConnect import *
from flask import render_template, Flask, request, redirect, url_for, flash
import webbrowser
from dotenv import load_dotenv
from helpers import *

project_folder = os.path.expanduser(os.path.abspath(os.path.curdir))  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

app = Flask(__name__)
app.secret_key = os.getenv("APP_KEY")


@app.route('/')
def home():
    last_backup_time = get_last_backup_time_from_file()
    return render_template('home.html', last_backup_time=last_backup_time)


@app.route('/add-patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        save_patient_func(request.form)
        return redirect(url_for('add_patient'))

    with sqlite3.connect("علاج.db") as connection:
        cursor = connection.cursor()
        try:
            cursor.execute("select max(الرقم_التسلسلي) from Patient")
            max_serial_num = cursor.fetchone()[0]
            if max_serial_num is None:
                max_serial_num = 2
            else:
                max_serial_num += 1
            connection.commit()
        except Exception as e:
            connection.rollback()
            flash('حدث خطأ أثناء الحصول على الرقم التسلسلي! \n' + str(e), 'error')
            print(e)
            last_backup_time = get_last_backup_time_from_file()
            return render_template('add-patient.html', last_backup_time=last_backup_time)
    
    year_num = datetime.now().year
    last_backup_time = get_last_backup_time_from_file()
    return render_template('add-patient.html', serial_num=max_serial_num, year_num=year_num, last_backup_time=last_backup_time)


@app.route('/update-patient', methods=['POST'])
def update_patient():
    result = save_patient_func(request.form, True)
    if type(result) is tuple:
        boolean, results = result
    else:
        boolean = result
        results = []
    last_backup_time = get_last_backup_time_from_file()
    return render_template('show-search-results.html', firstname=results[0], middlename=results[1], lastname=results[2], id=results[3], serialNum=results[4],
                        year=results[5], status=results[6], age=results[7], gender=results[8], children=results[9],
                        prayer=results[10], city=results[11], phone=results[12], work=results[13], health=results[14], companion=results[15],
                        description=results[16], diagnosis=results[17], therapy=results[18], last_backup_time=last_backup_time)


@app.route('/search-patient', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        status, results = search_patient_func(request.form['searchMethod'], request.form['search'], request.form['search1'])
        if type(results) is list and len(results) > 0:
            global data_dict
            data_dict = {}
            if status == 0:
                data_dict = {f'{row[SERIAL[1:]]}-{row[YEAR]}: {row[ALL_NAME]} - {row[CITY[1:]]}': row for row in results}
            last_backup_time = get_last_backup_time_from_file()
            return render_template('search-results.html', data=data_dict.keys(), last_backup_time=last_backup_time)
        else:
            flash("لم يتم إيجاد نتائج!", "error")
            return redirect(url_for('home'))
    else:
        last_backup_time = get_last_backup_time_from_file()
        return render_template("search-patient.html", last_backup_time=last_backup_time)


data_dict = {}


@app.route('/search-results', methods=['GET', 'POST'])
def search_results():
    last_backup_time = get_last_backup_time_from_file()
    return render_template('search-results.html', last_backup_time=last_backup_time)


@app.route('/show-search-results', methods=['GET', 'POST'])
def show_search_results():
    if request.form['searchResults'] == "---":
        flash("لا يوجد نتيجة!", "error")
        return redirect(url_for("home"))

    # fullname = data_dict[request.form['searchResults']][ALL_NAME].strip()
    # print(data_dict[request.form['searchResults']].keys())
    firstname = data_dict[request.form['searchResults']][FNAME].strip()
    middlename = data_dict[request.form['searchResults']][MNAME].strip()
    lastname = data_dict[request.form['searchResults']][LNAME].strip()
    id_number = data_dict[request.form['searchResults']][ID[1:]].strip()

    year_num = data_dict[request.form['searchResults']]["السنة"]
    serial_num = data_dict[request.form['searchResults']]["الرقم التسلسلي"]
    status = data_dict[request.form['searchResults']][STATUS[1:]].strip()
    age = data_dict[request.form['searchResults']][AGE[1:]].strip()
    gender = data_dict[request.form['searchResults']][GENDER[1:]].strip()
    children = data_dict[request.form['searchResults']][CHILDREN[1:]].strip()
    prayer = data_dict[request.form['searchResults']][PRAYER[1:]].strip()
    city = data_dict[request.form['searchResults']][CITY[1:]].strip()
    phone = data_dict[request.form['searchResults']][PHONE[1:]].strip()
    work = data_dict[request.form['searchResults']][WORK[1:]].strip()
    health = data_dict[request.form['searchResults']][HEALTH[1:]].strip()
    companion = data_dict[request.form['searchResults']][COMPANION[1:]].strip()
    description = data_dict[request.form['searchResults']][DESCRIPTION[1:]].strip()
    diagnosis = data_dict[request.form['searchResults']][DIAGNOSIS[1:]].strip()
    therapy = data_dict[request.form['searchResults']][THERAPY[1:]].strip()

    last_backup_time = get_last_backup_time_from_file()
    return render_template('show-search-results.html', firstname=firstname, middlename=middlename, lastname=lastname,
                           id=id_number, year_num=year_num, serialNum=serial_num, status=status, age=age,
                           gender=gender, children=children, prayer=prayer, city=city, phone=phone, work=work,
                           health=health, companion=companion, description=description, diagnosis=diagnosis, therapy=therapy, last_backup_time=last_backup_time)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.route('/save_to_GDrive', methods=["POST"])
def save_to_google_drive():
    save_func()
    update_last_backup_time_in_file(" جوجل درايف")
    return redirect(url_for("home"))


@app.route('/load_from_GDrive', methods=["POST"])
def load_from_google_drive():
    load_func()
    return redirect(url_for("home"))


@app.route('/xlsx_backup', methods=["POST"])
def xlsx_backup():
    do_backup_xlsx()
    return redirect(url_for("home"))


@app.route('/email_backup', methods=["POST"])
def email_backup():
    try:
        email = request.form.get("email")
        if email:
            do_backup_email(email)
            flash("تم الإرسال بنجاح!", "success")
        return redirect(url_for("home"))
    except Exception as e:
        flash("حدث خطأ أثناء الإرسال! \n" + str(e), "error")
        # print(e)
        return redirect(url_for("home"))


@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    if request.method == 'POST':
        os.kill(os.getpid(), signal.SIGINT)
    return render_template("shutdown.html")


if __name__ == "__main__":
    
    # drop_table()
    # create_table()

    if not os.path.exists("علاج.db"):
        create_table()
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
