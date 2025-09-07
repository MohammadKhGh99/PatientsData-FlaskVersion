from datetime import datetime
import os
import signal
import sqlite3
from Constants import *
from GDriveConnect import *
from flask import render_template, Flask, request, redirect, url_for, flash
import webbrowser


app = Flask(__name__)
app.secret_key = 'nglknfkgm;mf;gmn03h4w3t8409t'


@app.route('/')
def home():
    return render_template('home.html')


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
            return render_template('add-patient.html')
    
    year_num = datetime.now().year

    return render_template('add-patient.html', serial_num=max_serial_num, year_num=year_num)


@app.route('/update-patient', methods=['POST'])
def update_patient():
    result = save_patient_func(request.form, True)
    if type(result) is tuple:
        boolean, results = result
    else:
        boolean = result
        results = []
    return render_template('show-search-results.html', firstname=results[0], middlename=results[1], lastname=results[2], id=results[3], serialNum=results[4],
                        year=results[5], status=results[6], age=results[7], gender=results[8], children=results[9],
                        prayer=results[10], city=results[11], phone=results[12], work=results[13], health=results[14], companion=results[15],
                        description=results[16], diagnosis=results[17], therapy=results[18])


@app.route('/search-patient', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        status, results = search_patient_func(request.form['searchMethod'], request.form['search'], request.form['search1'])
        if type(results) is list and len(results) > 0:
            global data_dict
            data_dict = {}
            if status == 0:
                data_dict = {f'{row[SERIAL[1:]]}-{row[YEAR]}: {row[ALL_NAME]} - {row[CITY[1:]]}': row for row in results}
            return render_template('search-results.html', data=data_dict.keys())
        else:
            flash("لم يتم إيجاد نتائج!", "error")
            return redirect(url_for('home'))
    else:
        return render_template("search-patient.html")


data_dict = {}


@app.route('/search-results', methods=['GET', 'POST'])
def search_results():
    return render_template('search-results.html')


@app.route('/show-search-results', methods=['GET', 'POST'])
def show_search_results():
    if request.form['searchResults'] == "---":
        flash("لا يوجد نتيجة!", "error")
        return redirect(url_for("home"))

    # fullname = data_dict[request.form['searchResults']][ALL_NAME].strip()
    print(data_dict[request.form['searchResults']].keys())
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

    return render_template('show-search-results.html', firstname=firstname, middlename=middlename, lastname=lastname,
                           id=id_number, year_num=year_num, serialNum=serial_num, status=status, age=age,
                           gender=gender, children=children, prayer=prayer, city=city, phone=phone, work=work,
                           health=health, companion=companion, description=description, diagnosis=diagnosis, therapy=therapy)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


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


@app.route('/save_to_GDrive', methods=["POST"])
def save_to_google_drive():
    save_func()
    return redirect(url_for("home"))


@app.route('/load_from_GDrive', methods=["POST"])
def load_from_google_drive():
    load_func()
    return redirect(url_for("home"))


@app.route('/xlsx_backup', methods=["POST"])
def xlsx_backup():
    do_backup_xlsx()
    return redirect(url_for("home"))


@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    print("shutdown")
    if request.method == 'POST':
        os.kill(os.getpid(), signal.SIGINT)
    return render_template("shutdown.html")


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


if __name__ == "__main__":
    
    # drop_table()
    # create_table()

    if not os.path.exists("علاج.db"):
        create_table()
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
