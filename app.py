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
    fullname = form['fullname'].strip()
    id_number = form['id'].strip()
    serial_year_num = form['serialYearNum'].strip()
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
        splitted_name = fullname.split(' ')
        if len(splitted_name) == 3:
            first, middle, last = splitted_name
        else:
            first, last = splitted_name
            middle = ""
        if update:
            try:
                cursor.execute(f"update Patient "
                               f"set سنة_الرقم_التسلسلي = '{serial_year_num}',"
                               f"الرقم_التسلسلي = '{serial_num}',"
                               f"الإسم_الثلاثي = '{fullname}',"
                               f"الإسم_الشخصي = '{first}',"
                               f" إسم_الأب = '{middle}',"
                               f" إسم_العائلة = '{last}', "
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
                               f"where الرقم_التسلسلي = '{serial_num}' and الإسم_الثلاثي ='{fullname}'")
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
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (serial_year_num, serial_num, fullname, first, middle, last,
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
        return True, (fullname, id_number, serial_year_num, serial_num, status, age, gender, children, prayer, city, phone, work, health, companion, description, diagnosis, therapy)
    return True


@app.route('/add-patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        save_patient_func(request.form)
        return redirect(url_for('add_patient'))

    return render_template('add-patient.html')


@app.route('/update-patient', methods=['POST'])
def update_patient():
    result = save_patient_func(request.form, True)
    if type(result) is tuple:
        boolean, results = result
    else:
        boolean = result
        results = []
    return render_template('show-search-results.html', fullname=results[0], id=results[1], serialYearNum=results[2],
                        serialNum=results[3], status=results[4], age=results[5], gender=results[6], children=results[7],
                        prayer=results[8], city=results[9], phone=results[10], work=results[11], health=results[12], companion=results[13],
                        description=results[14], diagnosis=results[15], therapy=results[16])


@app.route('/search-patient', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        status, results = search_patient_func(request.form['searchMethod'], request.form['search'])
        if type(results) is list and len(results) > 0:
            global data_dict
            data_dict = {}
            if status == 0:
                data_dict = {f'{row[SERIAL[1:]]}: {row[ALL_NAME]} - {row[CITY[1:]]}': row for row in results}
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
    # if request.method == "POST":
    fullname = data_dict[request.form['searchResults']][ALL_NAME].strip()
    id_number = data_dict[request.form['searchResults']][ID[1:]].strip()

    serial_year_num = data_dict[request.form['searchResults']]["سنة الرقم التسلسلي"].strip()
    serial_num = data_dict[request.form['searchResults']]["الرقم التسلسلي"].strip()
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

    return render_template('show-search-results.html', fullname=fullname, id=id_number, serialYearNum=serial_year_num,
                           serialNum=serial_num, status=status, age=age, gender=gender, children=children,
                           prayer=prayer, city=city, phone=phone, work=work, health=health, companion=companion,
                           description=description, diagnosis=diagnosis, therapy=therapy)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


def search_patient_func(search_method, search_for=None):
    to_return = []
    with sqlite3.connect("علاج.db") as connection:
        cursor = connection.cursor()

        wanted_cols = 'الإسم_الثلاثي, رقم_الهوية, الجنس, الحالة_الإجتماعية, العمر, الرقم_التسلسلي, ' \
                      'سنة_الرقم_التسلسلي, أولاد, صلاة, صحة, العمل, المرافق, البلد, الهاتف, وصف_الحالة, التشخيص, العلاج'

        try:
            # taking all the patients
            if search_for is None or search_for.strip() == "":  # and (id_number is None or id_number.strip() == ""):
                cursor.execute(f"select {wanted_cols} from Patient")
                data = cursor.fetchall()
                connection.commit()
                for j in range(len(data)):
                    row = {ALL_DATA[i]: data[j][i] for i in range(len(ALL_DATA))}
                    to_return.append(row)
            else:
                if search_method == ID_SEARCH:
                    cursor.execute(
                        f"select {wanted_cols} from Patient where cast(رقم_الهوية as varchar(9)) = '{search_for}'")
                else:
                    if search_method == ALL_NAME:
                        cursor.execute(f"select {wanted_cols} from Patient where الإسم_الثلاثي = '{search_for}'")
                    elif search_method == FLNAME:
                        cur = search_for.split(" ")
                        cursor.execute(
                            f"select {wanted_cols} from Patient where الإسم_الشخصي = '{cur[0]}' and إسم_العائلة = '{cur[1]}'")
                    elif search_method == FMNAME:
                        cur = search_for.split(" ")
                        cursor.execute(
                            f"select {wanted_cols} from Patient where الإسم_الشخصي = '{cur[0]}' and إسم_الأب = '{cur[1]}'")
                    elif search_method == FNAME:
                        cursor.execute(f"select {wanted_cols} from Patient where الإسم_الشخصي = '{search_for}'")
                    elif search_method == LNAME:
                        cursor.execute(f"select {wanted_cols} from Patient where إسم_العائلة = '{search_for}'")
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
        سنة_الرقم_التسلسلي nvarchar(4),
        الرقم_التسلسلي nvarchar(20),
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
        وصف_الحالة nvarchar(200),
        التشخيص nvarchar(100),
        العلاج nvarchar(400)
    )
    """

    with sqlite3.connect("علاج.db") as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(arabic_sql_create_table)
            connection.commit()
        except Exception as e:
            flash(str(e), 'error')
            connection.rollback()
            print(e)


if __name__ == "__main__":
    # with sqlite3.connect("Patient.db") as data_connection:
    #     data_cursor = data_connection.cursor()
    #     data_cursor.execute("select * from Patient")
    #     all_data = data_cursor.fetchall()
    #     data_connection.commit()
    #     with sqlite3.connect("علاج.db") as empty_connection:
    #         empty_cursor = empty_connection.cursor()
    #         for data in all_data:
    #             empty_cursor.execute("insert into Patient values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    #                                 data)

    if not os.path.exists("علاج.db"):
        create_table()
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=False)
