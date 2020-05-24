from app import app
from flask import Flask, request, redirect, render_template, flash, url_for, session, send_from_directory, abort
import sys
sys.path.append('app/models')
sys.path.append('../data')
sys.path.append('app/code')
from user import User, UserLog
from plot import converttoDF
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import glob

@app.route("/signin", methods = ["GET", "POST"])
def signin():

    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")
        print(username, password)

        user = User()

        if user.check_password(username, password):
            user = User()
            user = user.get_user(username)

            # update last time logged in
            user.update_last_time_loggedin(datetime.now().replace(microsecond=0))

            session["SECRETKEY"] = user.secret_key
            flash("Signed in","success")

            # add action to user history
            user_log = UserLog(user.id, "signin", datetime.now().replace(microsecond=0))
            user_log.add()

            return redirect(url_for("welcome"))
        else:
            flash("Wrong credentials","danger")

    return render_template("public/signin.html")

def get_user():
    if session.get("SECRETKEY", None) is not None:
        secret_key = session.get('SECRETKEY')
        user = User()
        user = user.get_user_by_secret_key(secret_key)
        return user
    else:
        return None

@app.route("/", methods = ["GET", "POST"])
@app.route("/welcome")
def welcome():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user history
    user_log = UserLog(user.id, "welcome", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/welcome.html", username = user.username)

@app.route("/signout")
def signout():
    user = get_user()
    session.pop("SECRETKEY", None)

    # add action to user log
    user_log = UserLog(user.id, "signout", datetime.now().replace(microsecond=0))
    user_log.add()

    return redirect(url_for("signin"))

@app.route("/profile")
def profile():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "profile", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/profile.html", user = user)

@app.route("/download_obs/<file_name>")
def download_obs(file_name):
    try:
        return send_from_directory(app.config["OBS_FILES_DIR"], filename=file_name, as_attachment = True)
    except:
        abort(404)

@app.route("/download")
def download():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "download", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/download.htm", username = user.username)

def allowed_file(file_name):
    if not "." in file_name:
        return False
    ext = file_name.rsplit(".",1)[1]
    if ext.upper() in app.config["ALLOWED_FILE_EXTENTIONS"]:
        return True
    else:
        return False

@app.route("/upload_obs", methods=["GET","POST"])
def upload_obs():
    user =get_user()
    path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username)) + ("/obs")

    # create a directory for user
    if not os.path.exists(path):
        os.makedirs(path)

    if request.method == "POST":
        if request.files:
            obs = request.files["obs"]
            if obs.filename =="":
                flash("Select a file","danger")
                return redirect(url_for("upload"))

            if not allowed_file(obs.filename):
                flash("File extention not allowed","danger")
                return redirect(url_for("upload"))
            else:
                filename = secure_filename(obs.filename)
                obs.save(os.path.join(path, filename))
                flash("File uploaded", "success")
                return redirect(url_for("upload"))

@app.route("/check_files", methods = ["GET","POST"])
def check_files():
    user =get_user()
    path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username))+("/obs")

    # create a directory for user
    if not os.path.exists(path):
        os.makedirs(path)

    number_of_files = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

    if number_of_files == 2:
        return redirect(url_for("data_preview"))

    if number_of_files > 2:
        flash("It seems you have uploaded more than two files. Please upload only two files again.",'danger')
        # remove all files
        files = os.listdir(path)
        print('***********',files)
        for f in files:
            os.remove('{}/{}'.format(path,f))
        return redirect(url_for("upload"))

    if number_of_files == 1:
        flash("Please upload both files.",'danger')
        return redirect(url_for("upload"))

    if number_of_files < 1:
        flash("Please upload files.",'danger')
        return redirect(url_for("upload"))



@app.route("/upload")
def upload():
    user = get_user()
    try:
        path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username)) +("/obs")
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except:
        files = []

    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "upload", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/upload.html", username = user.username, files = files, file_count = len(files))

@app.route("/crhm")
def crhm():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "crhm", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/crhm.html", username = user.username)

@app.route("/data_preview", methods = ["GET", "POST"])
def data_preview():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))
    data_type = ""
    df1_html = ""
    df2_html = ""
    df3_html = ""
    df4_html = ""
    if request.method == "POST":
        req = request.form
        data_type = req.get("data_type")
        print('*************', data_type)
        # add action to user log
        user_log = UserLog(user.id, "data_preview", datetime.now().replace(microsecond=0))
        user_log.add()

        # convert obs file to df
        path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username)) + ("/obs")
        files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

        obs_file_1 = path + '/' + files[0]
        obs_file_2 = path + '/' + files[1]

        df1 = converttoDF(obs_file_1)
        df1_html = df1.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df2 = converttoDF(obs_file_2)
        df2_html = df2.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df3 = df1.merge(df2, on = 'time', how ='outer')
        df3_html = df3.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df4 = df1.merge(df2, how ='outer', left_index=True, right_index=True)
        df4_html = df4.to_html(classes="table table-hover table-striped table-sm table-bordered")

    return render_template("public/data_preview.html", username = user.username, data_type = data_type, df1 = df1_html, df2 = df2_html, df3 = df3_html, df4 = df4_html)


@app.route("/plot")
def plot():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "plot", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/plot.html", username = user.username)

@app.route("/questions")
def questions():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "questions", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/questions.html", username = user.username)

@app.route("/checkout")
def checkout():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "checkout", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/checkout.html", username = user.username)

@app.route("/finish")
def finish():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "finish", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/finish.html", username = user.username)