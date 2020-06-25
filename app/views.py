from app import app
from flask import Flask, request, redirect, render_template, flash, url_for, session, send_from_directory, abort
import sys
sys.path.append('app/models')
sys.path.append('../data')
sys.path.append('app/code')
from user import User, UserLog, NasaTLX
from plot import converttoDF, plot_go
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import glob
import webbrowser
import pandas as pd

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

@app.route("/consent_form", methods = ["GET", "POST"])
def consent_form():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user history
    user_log = UserLog(user.id, "consent_form", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/consent_form.html", username = user.username)

@app.route("/participants_info",methods = ["GET", "POST"])
def participants_info():
    user = get_user()
    if request.method == "POST":
        req = request.form
        age = req.get("age")
        gender = req.get("genderRadios")
        crhm_exp = req.get("crhmRadios")
        dev_exp = req.get("dev_exp")
        test_exp = req.get("test_exp")
        role_exp = req.get("role_exp")
        if age == user.age and crhm_exp == user.crhm_exp and gender == user.gender and dev_exp == user.dev_exp_years and test_exp == user.test_exp_years and role_exp == user.role_exp:
            return redirect("download")
        else:
            user.update_userInfo(age, crhm_exp, gender, dev_exp, test_exp, role_exp)
            flash("Information saved successfully","success")
            return redirect("download")

    return render_template("public/participants_info.html", username = user.username, crhm_exp = user.crhm_exp, gender = user.gender, age = user.age, dev_exp = user.dev_exp_years, test_exp = user.test_exp_years, role = user.role_exp)

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

@app.route("/download_crhm")
def download_crhm():
    try:
        return send_from_directory(app.config["CRHM_APP_DIR"], filename='crhm.zip', as_attachment = True)
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

    if user is None:
        return redirect(url_for("signin"))

    try:
        path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username)) +("/obs")
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except:
        files = []

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

@app.route("/crhm_guid")
def crhm_guid():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "crhm_guid", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/crhm_guid.html", username = user.username)

def highlight_greaterthan(s,threshold,column):
    is_max = pd.Series(data=False, index=s.index)
    is_max[column] = s.loc[column] >= threshold
    return ['background-color: yellow' if is_max.any() else '' for v in is_max]

@app.route("/crhm_tlx",methods = ["GET", "POST"])
def crhm_tlx():
    user = get_user()

    if user is None:
        return redirect(url_for("signin"))

    questions = [['How mental demanding was the task?','mental'],['How physically demanding was the task?','physical'], ['How hurried or rushed was the pace of the task?','hurried'],
                    ['How successful were you in accomplishing what you were asked to do?','accomplish'], ['How hard did you have to work to accomplish your level of performance?', 'performance'],
                    ['How insecure, discouraged, irritated stressed and annoyed were you?', 'insecure']]
    answers = range(1,11)

    if request.method == "POST":
        req = request.form
        crhm_nasa_tlx = NasaTLX(user.id,'crhm' ,req.get("mental"), req.get("physical"), req.get("hurried"), req.get("accomplish"), req.get("performance"), req.get("insecure"))
        crhm_nasa_tlx.add()
        return redirect("new_intro")

    return render_template("public/crhm_tlx.html", username = user.username, answers = answers, questions = questions)

@app.route("/new_intro")
def new_intro():
    user = get_user()

    if user is None:
        return redirect(url_for("signin"))

    return render_template("public/new_intro.html")

@app.route("/new_tlx",methods = ["GET", "POST"])
def new_tlx():
    user = get_user()

    if user is None:
        return redirect(url_for("signin"))

    questions = [['How mental demanding was the task?','mental'],['How physically demanding was the task?','physical'], ['How hurried or rushed was the pace of the task?','hurried'],
                    ['How successful were you in accomplishing what you were asked to do?','accomplish'], ['How hard did you have to work to accomplish your level of performance?', 'performance'],
                    ['How insecure, discouraged, irritated stressed and annoyed were you?', 'insecure']]
    answers = range(1,11)

    if request.method == "POST":
        req = request.form
        crhm_nasa_tlx = NasaTLX(user.id,'new' ,req.get("mental"), req.get("physical"), req.get("hurried"), req.get("accomplish"), req.get("performance"), req.get("insecure"))
        crhm_nasa_tlx.add()
        return redirect('checkout')

    return render_template("public/new_tlx.html", username = user.username, answers = answers, questions = questions)



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

        df1['SWE(1) 1'] = df1['SWE(1) 1'].astype(float)
        df1_style = df1.style.apply(highlight_greaterthan,threshold=1.0,column=['SWE(1) 1'], axis=1)
        #print('********************************',df1_style.render())
        df1_html = df1_style.render(classes="table table-hover table-striped table-sm table-bordered") #df1.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df2 = converttoDF(obs_file_2)
        df2_html = df2.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df3 = df1.merge(df2, on = 'time', how ='outer')
        df3_html = df3.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df4 = df1.merge(df2, how ='outer', left_index=True, right_index=True)
        df4_html = df4.to_html(classes="table table-hover table-striped table-sm table-bordered")

    return render_template("public/data_preview.html", username = user.username, data_type = data_type, df1 = df1_html, df2 = df2_html, df3 = df3_html, df4 = df4_html)


@app.route("/data_preview_expanded", methods = ["GET", "POST"])
def data_preview_expanded():
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

    return render_template("public/data_preview_expanded.html", username = user.username, data_type = data_type, df1 = df1_html, df2 = df2_html, df3 = df3_html, df4 = df4_html)

@app.route("/show_plot", methods = ["GET", "POST"])
def show_plot():
    user = get_user()

    path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username)) + ("/obs")
    html_path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username))
    files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

    obs_file_1 = path + '/' + files[0]
    obs_file_2 = path + '/' + files[1]


    df1 = converttoDF(obs_file_1)
    df2 = converttoDF(obs_file_2)
    df3 = df1.merge(df2, on = 'time', how ='outer')

    plot_go(df3,'test', html_path)

    return render_template("public/plot.html", username = user.username)

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

@app.route("/checkout", methods = ["GET", "POST"])
def checkout():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    if request.method == "POST":
        req = request.form
        user = get_user()
        email = req.get("email")
        user.update_userEmail(email)
        flash("Email saved successfully","success")
        return render_template("public/finish.html")

    # add action to user log
    user_log = UserLog(user.id, "checkout", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/checkout.html", username = user.username, email = user.email)

@app.route("/finish")
def finish():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))

    # add action to user log
    user_log = UserLog(user.id, "finish", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/finish.html", username = user.username)