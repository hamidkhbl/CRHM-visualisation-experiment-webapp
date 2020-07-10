from app import app
from flask import Flask, request, redirect, render_template, flash, url_for, session, send_from_directory, abort, Blueprint
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
from flask_login import login_user, current_user, logout_user, login_required

users = Blueprint('users', __name__)

@users.route("/signin", methods = ["GET", "POST"])
def signin():

    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")

        user = User()

        if user.check_password(username, password):
            user = User()
            user = user.get_user(username)

            # update last time logged in
            user.update_last_time_loggedin(datetime.now().replace(microsecond=0))

            login_user(user)
            next_page = request.args.get('next')

            #session["SECRETKEY"] = user.secret_key
            #flash("Signed in","success")

            # add action to user history
            user_log = UserLog(user.id, "signin", datetime.now().replace(microsecond=0))
            user_log.add()

            #return redirect(next_page) if next_page else redirect(url_for("users.welcome"))
            return redirect(url_for("users.welcome"))
        else:
            flash("Wrong credentials","danger")
            return redirect(url_for("users.signin"))

    return render_template("public/signin.html")

def get_user():
    if current_user.is_authenticated:
        user = User()
        user = user.get_user(current_user.username)
        return user
    else:
        return None



@users.route("/", methods = ["GET", "POST"])
@users.route("/welcome")
@login_required
def welcome():
    user = get_user()

    #add action to user history
    user_log = UserLog(user.id, "welcome", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/welcome.html")

@users.route("/consent_form", methods = ["GET", "POST"])
@login_required
def consent_form():
    user = get_user()

    # add action to user history
    user_log = UserLog(user.id, "consent_form", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/consent_form.html")

@users.route("/participants_info",methods = ["GET", "POST"])
@login_required
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
        degree = req.get("degree")

        if degree == user.degree and age == user.age and crhm_exp == user.crhm_exp and gender == user.gender and dev_exp == user.dev_exp_years and test_exp == user.test_exp_years and role_exp == user.role_exp:
            return redirect("download")
        else:
            user.update_userInfo(age, crhm_exp, gender, dev_exp, test_exp, role_exp, degree)
            flash("Information saved successfully","success")
            return redirect("download")

    return render_template("public/participants_info.html", crhm_exp = user.crhm_exp, gender = user.gender, age = user.age, dev_exp = user.dev_exp_years, test_exp = user.test_exp_years, role = user.role_exp, degree = user.degree)

@users.route("/signout")
@login_required
def signout():
    user = get_user()
    logout_user()

    # add action to user log
    user_log = UserLog(user.id, "signout", datetime.now().replace(microsecond=0))
    user_log.add()

    return redirect(url_for("users.signin"))

@users.route("/profile")
@login_required
def profile():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "profile", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/profile.html", user = user)


@users.route("/download_obs/<file_name>")
@login_required
def download_obs(file_name):
    try:
        return send_from_directory(app.config["OBS_FILES_DIR"], filename=file_name, as_attachment = True)
    except:
        abort(404)

@users.route("/download_crhm")
def download_crhm():
    try:
        return send_from_directory(app.config["CRHM_APP_DIR"], filename='crhm.zip', as_attachment = True)
    except:
        abort(404)

@users.route("/download")
@login_required
def download():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "download", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/download.htm")

def allowed_file(file_name):
    if not "." in file_name:
        return False
    ext = file_name.rsplit(".",1)[1]
    if ext.upper() in app.config["ALLOWED_FILE_EXTENTIONS"]:
        return True
    else:
        return False

@users.route("/upload_obs", methods=["GET","POST"])
@login_required
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
                return redirect(url_for("users.upload"))

            if not allowed_file(obs.filename):
                flash("File extention not allowed","danger")
                return redirect(url_for("users.upload"))
            else:
                filename = secure_filename(obs.filename)
                obs.save(os.path.join(path, filename))
                flash("File uploaded", "success")
                return redirect(url_for("users.upload"))

@users.route("/check_files", methods = ["GET","POST"])
@login_required
def check_files():
    user =get_user()

    path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username))+("/obs")

    # create a directory for user
    if not os.path.exists(path):
        os.makedirs(path)

    number_of_files = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

    if number_of_files == 2:
        return redirect(url_for("users.data_preview"))

    if number_of_files > 2:
        flash("It seems you have uploaded more than two files. Please upload only two files again.",'danger')
        # remove all files
        files = os.listdir(path)

        for f in files:
            os.remove('{}/{}'.format(path,f))
        return redirect(url_for("users.upload"))

    if number_of_files == 1:
        flash("Please upload both files.",'danger')
        return redirect(url_for("users.upload"))

    if number_of_files < 1:
        flash("Please upload files.",'danger')
        return redirect(url_for("users.upload"))



@users.route("/upload")
@login_required
def upload():
    user = get_user()

    try:
        path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username)) +("/obs")
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except:
        files = []

    # add action to user log
    user_log = UserLog(user.id, "upload", datetime.now().replace(microsecond=0))
    user_log.add()
    return render_template("public/upload.html", files = files, file_count = len(files))

@users.route("/crhm")
@login_required
def crhm():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "crhm", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/crhm.html")

@users.route("/crhm_guid")
@login_required
def crhm_guid():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "crhm_guid", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/crhm_guid.html")

def highlight_greaterthan(s,threshold,column):
    is_max = pd.Series(data=False, index=s.index)
    is_max[column] = s.loc[column] >= threshold
    return ['background-color: yellow' if is_max.any() else '' for v in is_max]

@users.route("/crhm_tlx",methods = ["GET", "POST"])
def crhm_tlx():
    user = get_user()

    tlx = NasaTLX.get_user_tlx(userId = user.id, page = 'crhm')

    questions = [['How mental demanding was the task?','mental_demanding'],
                    ['How physically demanding was the task?','physically_demanding'],
                    ['How hurried or rushed was the pace of the task?','hurried_rushed'],
                    ['How successful were you in accomplishing what you were asked to do?','successful_accomplishing'],
                    ['How hard did you have to work to accomplish your level of performance?', 'hard_performance'],
                    ['How insecure, discouraged, irritated stressed and annoyed were you?', 'insecure_discouraged']]
    answers = range(1,11)

    if tlx is not None:
        questions = [['How mental demanding was the task?','mental_demanding',int(tlx.mental_demanding)],
                    ['How physically demanding was the task?','physically_demanding',int(tlx.physically_demanding)],
                    ['How hurried or rushed was the pace of the task?','hurried_rushed',int(tlx.hurried_rushed)],
                    ['How successful were you in accomplishing what you were asked to do?','successful_accomplishing',int(tlx.successful_accomplishing)],
                    ['How hard did you have to work to accomplish your level of performance?', 'hard_performance', int(tlx.hard_performance)],
                    ['How insecure, discouraged, irritated stressed and annoyed were you?', 'insecure_discouraged', int(tlx.insecure_discouraged)]]
        answers = range(1,11)

    if request.method == "POST":
        req = request.form
        crhm_nasa_tlx = NasaTLX(user.id,'crhm' ,req.get("mental_demanding"), req.get("physically_demanding"), req.get("hurried_rushed"), req.get("successful_accomplishing"), req.get("hard_performance"), req.get("insecure_discouraged"), req.get("crhm_time"), req.get("crhm_mismatch"))
        if tlx is None:
            crhm_nasa_tlx.add()
        else:
            tlx.update_user_tlx(req.get("mental_demanding"), req.get("physically_demanding"), req.get("hurried_rushed"), req.get("successful_accomplishing"), req.get("hard_performance"), req.get("insecure_discouraged"), req.get("crhm_time"), req.get("crhm_mismatch"))

        return redirect("new_intro")

    return render_template("public/crhm_tlx.html", answers = answers, questions = questions, time = tlx.time, mismatch = tlx.mismatch)

@users.route("/new_intro")
@login_required
def new_intro():
    user = get_user()

    return render_template("public/new_intro.html")

@users.route("/new_tlx",methods = ["GET", "POST"])
def new_tlx():
    user = get_user()

    tlx = NasaTLX.get_user_tlx(userId = user.id, page = 'new')

    questions = [['How mental demanding was the task?','mental_demanding'],
                    ['How physically demanding was the task?','physically_demanding'],
                    ['How hurried or rushed was the pace of the task?','hurried_rushed'],
                    ['How successful were you in accomplishing what you were asked to do?','successful_accomplishing'],
                    ['How hard did you have to work to accomplish your level of performance?', 'hard_performance'],
                    ['How insecure, discouraged, irritated stressed and annoyed were you?', 'insecure_discouraged']]
    answers = range(1,11)

    if tlx is not None:
        questions = [['How mental demanding was the task?','mental_demanding',int(tlx.mental_demanding)],
                    ['How physically demanding was the task?','physically_demanding',int(tlx.physically_demanding)],
                    ['How hurried or rushed was the pace of the task?','hurried_rushed',int(tlx.hurried_rushed)],
                    ['How successful were you in accomplishing what you were asked to do?','successful_accomplishing',int(tlx.successful_accomplishing)],
                    ['How hard did you have to work to accomplish your level of performance?', 'hard_performance', int(tlx.hard_performance)],
                    ['How insecure, discouraged, irritated stressed and annoyed were you?', 'insecure_discouraged', int(tlx.insecure_discouraged)]]
        answers = range(1,11)

    if request.method == "POST":
        req = request.form
        new_nasa_tlx = NasaTLX(user.id,'new' ,req.get("mental_demanding"), req.get("physically_demanding"), req.get("hurried_rushed"), req.get("successful_accomplishing"), req.get("hard_performance"), req.get("insecure_discouraged"), req.get("new_time"), req.get("new_mismatch"))
        if tlx is None:
            new_nasa_tlx.add()
        else:
            tlx.update_user_tlx(req.get("mental_demanding"), req.get("physically_demanding"), req.get("hurried_rushed"), req.get("successful_accomplishing"), req.get("hard_performance"), req.get("insecure_discouraged"), req.get("new_time"), req.get("new_mismatch"))

        return redirect("checkout")

    return render_template("public/new_tlx.html", answers = answers, questions = questions, time = tlx.time, mismatch = tlx.mismatch)



@users.route("/data_preview", methods = ["GET", "POST"])
@login_required
def data_preview():
    user = get_user()

    data_type = ""
    df1_html = ""
    df2_html = ""
    df3_html = ""
    df4_html = ""
    if request.method == "POST":
        req = request.form
        data_type = req.get("data_type")
        # add action to user log
        user_log = UserLog(user.id, "data_preview", datetime.now().replace(microsecond=0))
        user_log.add()

        # convert obs file to df
        path = os.path.join(app.config["OBS_FILES_DIR"]) #+ ("/{}".format(user.username)) + ("/obs")
        files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

        obs_file_1 = path + '/' + files[0]
        obs_file_2 = path + '/' + files[1]

        df1 = converttoDF(obs_file_1)

        df1['SWE(1) 1'] = df1['SWE(1) 1'].astype(float)
        df1_style = df1.style.apply(highlight_greaterthan,threshold=1.0,column=['SWE(1) 1'], axis=1)

        df1_html = df1_style.render(classes="table table-hover table-striped table-sm table-bordered") #df1.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df2 = converttoDF(obs_file_2)
        df2_html = df2.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df3 = df1.merge(df2, on = 'time', how ='outer')
        df3_html = df3.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df4 = df1.merge(df2, how ='outer', left_index=True, right_index=True)
        df4_html = df4.to_html(classes="table table-hover table-striped table-sm table-bordered")

    return render_template("public/data_preview.html", data_type = data_type, df1 = df1_html, df2 = df2_html, df3 = df3_html, df4 = df4_html)


@users.route("/data_preview_expanded", methods = ["GET", "POST"])
@login_required
def data_preview_expanded():
    user = get_user()

    data_type = ""
    df1_html = ""
    df2_html = ""
    df3_html = ""
    df4_html = ""
    if request.method == "POST":
        req = request.form
        data_type = req.get("data_type")
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

    return render_template("public/data_preview_expanded.html", data_type = data_type, df1 = df1_html, df2 = df2_html, df3 = df3_html, df4 = df4_html)

@users.route("/show_plot", methods = ["GET", "POST"])
@login_required
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

    plot_go(df3,'Data from both files are plotted here', html_path)

    return render_template("public/plot.html")

@users.route("/plot")
@login_required
def plot():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "plot", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/plot.html")

@users.route("/questions")
@login_required
def questions():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "questions", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/questions.html")

@users.route("/checkout", methods = ["GET", "POST"])
@login_required
def checkout():
    user = get_user()

    if request.method == "POST":
        req = request.form
        user = get_user()
        email = req.get("email")
        one_sitting = req.get("one_sitting")
        task1_like = req.get("task1_like")
        task2_like = req.get("task2_like")

        if email != user.email or one_sitting != user.one_sitting or task1_like != user.task1_like or task2_like != user.task2_like:
            user.update_user_checkout_Info(email, one_sitting, task1_like, task2_like)
            flash("Email saved successfully","success")
        return redirect("finish")

    # add action to user log
    user_log = UserLog(user.id, "checkout", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/checkout.html", email = user.email, one_sitting = user.one_sitting, task1_like = user.task1_like, task2_like = user.task2_like)

@users.route("/finish")
@login_required
def finish():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "finish", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/finish.html")
