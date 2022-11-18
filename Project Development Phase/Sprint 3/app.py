import math
import random

import ibm_db
from cryptography.hazmat.backends import default_backend
from flask import Flask, render_template, request, session, redirect

from markupsafe import escape

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif'}

conn = ibm_db.connect(
    "DATABASE=bludb;HOSTNAME=ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT"
    "=31505;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xnc98967;PWD=wQioPYLq4Oanh0Vm",
    '', '')

print(conn)

# key for encryption
KEY = "xxxxxxxxxxxxxxxxxxxxx"
# sendgrid
SENDGRID_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

app = Flask(__name__)

app.secret_key = "\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"

backend = default_backend()


def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


def get_history():
    history = []
    sql = f"SELECT * FROM PERSON WHERE email = '{session['email']}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary:
        history.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return history


def get_history_person(email):
    history = []
    sql = f"SELECT * FROM PERSON WHERE email = '{email}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary:
        history.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return history


def get_history_person_time(time):
    historys = []
    sql = f"SELECT * FROM PERSON WHERE time = '{time}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary:
        historys.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return historys


def get_user():
    user = []
    sql = f"SELECT * FROM USER"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary:
        user.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return user



@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST' and 'email' in request.form and 'pass' in request.form:
        error = None
        email = request.form['email']
        password = request.form['pass']
        user = None
        return render_template('dashboard.html', user=user, email=email, history=get_history())

    elif request.method == 'POST' and 'deleteHistory' in request.form:
        sql = f"SELECT * FROM PERSON WHERE email='{session['email']}'"
        print(sql)
        stmt = ibm_db.exec_immediate(conn, sql)
        list_of_history = ibm_db.fetch_row(stmt)
        if list_of_history:
            sql = f"DELETE FROM PERSON WHERE email='{session['email']}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            history = get_history()
            if history:
                return render_template("dashboard.html", msg="Delete successfully", user=session['name'],
                                       email=session['email'])

        return render_template("dashboard.html", msg="Delete successfully", user=session['name'],
                               email=session['email'])

    elif request.method == 'POST' and 'logout' in request.form:
        session["loggedIn"] = None
        session['name'] = None
        session['email'] = None
        return render_template('index.html', error="Successfully Logged Out!")

    elif request.method == 'POST' and 'extra_submit_param_view' in request.form:
        nutrition_list = request.form["extra_submit_param_view"]
        history = get_history()
        splitted_nutrition = nutrition_list.split(",")
        return render_template('dashboard.html', user=session['name'], email=session['email'], data=splitted_nutrition,
                               history=history)

    elif request.method == 'POST' and 'extra_submit_param_delete' in request.form:
        time_identity = request.form["extra_submit_param_delete"]
        history = get_history()
        sql = f"SELECT * FROM PERSON WHERE time='{escape(time_identity)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        row = ibm_db.fetch_row(stmt)
        if row:
            sql = f"DELETE FROM PERSON WHERE time='{escape(time_identity)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            history = get_history()
            if history:
                return render_template("dashboard.html", history=history, msg="Delete successfully")
            return render_template("dashboard.html", msg="Delete successfully")
        return render_template("dashboard.html", history=history, msg="Something went wrong, Try again")

    elif request.method == 'POST' and 'extra_submit_param_record' in request.form:
        email_user = request.form["extra_submit_param_record"]
        return render_template('adminpanal.html', user=session['name'], email=session['email'], list=get_user(),
                               history=get_history_person(email_user))

    elif request.method == 'POST' and 'extra_submit_param_delete_user' in request.form:
        email_user = request.form["extra_submit_param_delete_user"]
        sql = f"SELECT * FROM USER WHERE time='{escape(email_user)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        row = ibm_db.fetch_row(stmt)
        if row:
            sql = f"DELETE FROM USER WHERE time='{escape(email_user)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
        sql = f"SELECT * FROM PERSON WHERE time='{escape(email_user)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        row = ibm_db.fetch_row(stmt)
        if row:
            sql = f"DELETE FROM PERSON WHERE time='{escape(email_user)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
        return render_template('adminpanal.html', user=session['name'], list=get_user())

    elif request.method == 'POST' and 'extra_submit_param_nutritions' in request.form:
        user_time = request.form["extra_submit_param_nutritions"]
        user_of = get_history_person_time(user_time)
        user_dic = user_of[0]
        splitted_nutrition = user_dic['NUTRITION'].split(",")
        return render_template('adminpanal.html', user=session['name'], list=get_user(),
                               history=get_history_person(user_dic["EMAIL"]), data=splitted_nutrition)

    elif request.method == 'POST' and 'extra_submit_param_delete_record' in request.form:
        email_user = request.form["extra_submit_param_delete_record"]
        user_of = get_history_person_time(email_user)
        user_dic = user_of[0]
        sql = f"SELECT * FROM PERSON WHERE time='{escape(email_user)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        row = ibm_db.fetch_row(stmt)
        if row:
            sql = f"DELETE FROM PERSON WHERE time='{escape(email_user)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
        return render_template('adminpanal.html', user=session['name'], list=get_user(),
                               history=get_history_person(user_dic["EMAIL"]))

    elif session.get('loggedIn'):
        history = get_history()
        return render_template('dashboard.html', user=session['name'], history=history)
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/dashboard', methods=['GET', 'POST'])
def upload_file():
    history = []
    # sql = "SELECT * FROM Students"
    sql = f"SELECT * FROM PERSON WHERE email = '{session['email']}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary:
        history.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'logout' in request.form:
            session["loggedIn"] = None
            session['name'] = None
            session['email'] = None
            return render_template('index.html', error="Successfully created")
        if 'file' not in request.files:
            # flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        if file.filename == '':
            return render_template('dashboard.html', msg="File not found", history=history)
        baseimage = file.read()
        if file and allowed_file(file.filename):
            pass
        return render_template('dashboard.html', history=history)
    if session['name'] is None:
        return render_template('index.html')
    return render_template('dashboard.html', user=session['name'], email=session['email'], history=history)


if __name__ == '__main__':
    app.debug = True
    app.run()
