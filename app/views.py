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

@users.route("/")
@users.route("/signin", methods = ["GET", "POST"])
def signin():

    if request.method == "POST":
        req = request.form
        username = req.get("username").lower()
        password = req.get("password")

        user = User()


        if user.check_password(username, password):
            user = User()
            user = user.get_user(username)

            if user.check_active(username):

                # update last time logged in
                user.update_last_time_loggedin(datetime.now().replace(microsecond=0))

                login_user(user)

                # add action to user history
                user_log = UserLog(user.id, "signin", datetime.now().replace(microsecond=0))
                user_log.add()

                return redirect(url_for("users.dashboard"))
            else:
                flash("Your user has been deactivated.","danger")
                return redirect(url_for("users.signin"))

        else:
            flash("Wrong credentials","danger")
            return redirect(url_for("users.signin"))

    return render_template("public/signin.html")

def get_user():
    if current_user.is_authenticated:
        user = User()
        user = user.get_user(current_user.username)
        print('*****************', os.path.basename(request.path))
        return user
    else:
        print('*****************', os.path.basename(request.path))
        return None


@users.route("/dashboard", methods = ["GET", "POST"])
@login_required
def dashboard():
    user = get_user()

    # add action to user history
    user_log = UserLog(user.id, "dashboard", datetime.now().replace(microsecond=0))
    user_log.add()

    try:
        path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username)) +("/obs")
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    except:
        files = []

    return render_template("public/dashboard.html", files = files, file_count = len(files))

@users.route('/delete_file/<file_name>', methods=['GET', 'POST'])
@login_required
def delete_file(file_name):
    user = get_user()
    os.remove(app.config["FILE_UPLOADS"] + ("/{}".format(user.username)) +("/obs/"+file_name))
    flash("File deleted.","primary")
    return redirect(url_for('users.dashboard'))

@users.route("/welcome", methods = ["GET", "POST"])
#@login_required
def welcome():
    user = get_user()

    #add action to user history
    user_log = UserLog(user.id, "welcome", datetime.now().replace(microsecond=0))
    user_log.add()
    page = Page()
    if request.method == "POST":
        req = request.form
        return redirect(url_for(page.page_handler('next',user)))

    return render_template("public/welcome.html", page=page.get_page_number(user))

@users.route("/consent_form", methods = ["GET", "POST"])
@login_required
def consent_form():
    user = get_user()

    # add action to user history
    user_log = UserLog(user.id, "consent_form", datetime.now().replace(microsecond=0))
    user_log.add()
    page = Page()

    if request.method == "POST":
        return redirect(url_for(page.page_handler('next',user)))

    return render_template("public/consent_form.html", page=page.get_page_number(user))

@users.route("/participants_info",methods = ["GET", "POST"])
@login_required
def participants_info():
    user = get_user()

    # add action to user history
    user_log = UserLog(user.id, "participants_info", datetime.now().replace(microsecond=0))
    user_log.add()
    page=Page()

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
            return redirect(url_for(page.page_handler('next',user)))
        else:
            user.update_userInfo(age, crhm_exp, gender, dev_exp, test_exp, role_exp, degree)
            flash("Information saved successfully","success")
            return redirect(url_for(page.page_handler('next',user)))

    return render_template("public/participants_info.html", crhm_exp = user.crhm_exp, gender = user.gender, age = user.age, dev_exp = user.dev_exp_years, test_exp = user.test_exp_years, role = user.role_exp if user.role_exp is not None else '', degree = user.degree, page=page.get_page_number(user))

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
    user = get_user()
    # add action to user history
    user_log = UserLog(user.id, "download_"+file_name, datetime.now().replace(microsecond=0))
    user_log.add()
    try:
        return send_from_directory(app.config["OBS_FILES_DIR"], filename=file_name, as_attachment = True)
    except:
        abort(404)

@users.route("/download_crhm")
def download_crhm():
    user = get_user()
    # add action to user history
    user_log = UserLog(user.id, "download_crhm", datetime.now().replace(microsecond=0))
    user_log.add()
    try:
        return send_from_directory(app.config["CRHM_APP_DIR"], filename='crhm.zip', as_attachment = True)
    except:
        abort(404)

@users.route("/download",methods = ["GET", "POST"])
@login_required
def download():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "download", datetime.now().replace(microsecond=0))
    user_log.add()
    page = Page()

    if request.method == "POST":
        return redirect(url_for(page.page_handler('back',user)))


    return render_template("public/download.htm", page=page.get_page_number(user))

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


    # add action to user history
    user_log = UserLog(user.id, "upload_obs", datetime.now().replace(microsecond=0))
    user_log.add()

    path = os.path.join(app.config["FILE_UPLOADS"]) + ("/{}".format(user.username)) + ("/obs")

    # create a directory for user
    if not os.path.exists(path):
        os.makedirs(path)

    if request.method == "POST":
        if request.files:
            obs = request.files["obs_input"]
            if obs.filename =="":
                flash("Select a file","danger")
                return redirect(url_for("users.dashboard"))

            if not allowed_file(obs.filename):
                flash("File extention not allowed","danger")
                return redirect(url_for("users.dashboard"))
            else:
                path = os.path.join(app.config["OBS_FILES_DIR"]) + ("/{}".format(user.username))+("/obs")
                number_of_files = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
                if number_of_files >= 2:
                    flash("Too many files!","danger")
                    return redirect(url_for("users.dashboard"))
                else:
                    filename = secure_filename(obs.filename)
                    obs.save(os.path.join(path, filename))
                    flash("File uploaded", "success")
                    return redirect(url_for("users.dashboard"))




@users.route("/check_files", methods = ["GET","POST"])
@login_required
def check_files():
    user =get_user()

    path = os.path.join(app.config["OBS_FILES_DIR"]) + ("/{}".format(user.username))+("/obs")

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

    # add action to user history
    user_log = UserLog(user.id, "upload", datetime.now().replace(microsecond=0))
    user_log.add()
    page=Page()

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
    page = Page()

    return render_template("public/crhm.html", page=page.get_page_number(user))

@users.route("/crhm_guid")
@login_required
def crhm_guid():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "crhm_guid", datetime.now().replace(microsecond=0))
    user_log.add()
    page = Page()

    return render_template("public/crhm_guid.html", page=page.get_page_number(user))

@users.route("/crhm_tlx",methods = ["GET", "POST"])
def crhm_tlx():
    user = get_user()

    # add action to user history
    user_log = UserLog(user.id, "crhm.tlx", datetime.now().replace(microsecond=0))
    user_log.add()
    page = Page()

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

        return redirect(url_for(page.page_handler('next',user)))

    return render_template("public/crhm_tlx.html", answers = answers, questions = questions, time = tlx.time if tlx is not None else '', mismatch = tlx.mismatch if tlx is not None else '', page=page.get_page_number(user))

@users.route("/new_intro",methods = ["GET", "POST"])
@login_required
def new_intro():
    user = get_user()

    # add action to user history
    user_log = UserLog(user.id, "new_intro", datetime.now().replace(microsecond=0))
    user_log.add()
    page = Page()
    if request.method == "POST":
        return redirect(url_for(page.page_handler('back',user)))

    return render_template("public/new_intro.html", page=page.get_page_number(user))

@users.route("/new_tlx",methods = ["GET", "POST"])
def new_tlx():
    user = get_user()

    # add action to user history
    user_log = UserLog(user.id, "new_txl", datetime.now().replace(microsecond=0))
    user_log.add()
    page=Page()

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

        return redirect(url_for(page.page_handler('next',user)))

    return render_template("public/new_tlx.html", answers = answers, questions = questions, time = tlx.time if tlx is not None else '', mismatch = tlx.mismatch if tlx is not None else '', page=page.get_page_number(user))

def highlight_diff(s,threshold,column):
    is_max = pd.Series(data=False, index=s.index)
    is_max[column] = abs(s.loc[column[1]] - s.loc[column[4]]) + abs(s.loc[column[2]] - s.loc[column[5]]) + abs(s.loc[column[3]] - s.loc[column[6]]) >= threshold
    return ['background-color: yellow' if is_max.any() else '' for v in is_max]


@users.route("/data_preview", methods = ["GET", "POST"])
@login_required
def data_preview():
    user = get_user()
    page = Page()

    data_type = ""
    df3_html = ""
    if request.method == "POST":
        req = request.form
        data_type = req.get("data_type")
        # add action to user log
        user_log = UserLog(user.id, "data_preview", datetime.now().replace(microsecond=0))
        user_log.add()

        # convert obs file to df
        path = os.path.join(app.config["OBS_FILES_DIR"]) #+ ("/{}".format(user.username)) + ("/obs")
        files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

        obs_file_1 = path + '/' + 'file1.obs'
        obs_file_2 = path + '/' + 'file2.obs'

        df1 = converttoDF(obs_file_1)
        df2 = converttoDF(obs_file_2)
        df1[df1.columns[1]] = df1[df1.columns[1]].astype(float)
        df1[df1.columns[2]] = df1[df1.columns[2]].astype(float)
        df1[df1.columns[3]] = df1[df1.columns[3]].astype(float)
        df2[df2.columns[1]] = df2[df2.columns[1]].astype(float)
        df2[df2.columns[2]] = df2[df2.columns[2]].astype(float)
        df2[df2.columns[3]] = df2[df2.columns[3]].astype(float)

        #df1['SWE(1) 1'] = df1['SWE(1) 1'].astype(float)
        #df1_style = df1.style.apply(highlight_diff_2,threshold=0,column_1=df1.columns, column_2=df2.columns, axis=1)

        #df1_html = df1_style.render(classes="table table-hover table-striped table-sm table-bordered")
        #df1.to_html(classes="table table-hover table-striped table-sm table-bordered")


        #df2_html = df2.to_html(classes="table table-hover table-striped table-sm table-bordered")

        df3 = df1.merge(df2, on = 'time', how ='outer')

        df3_style = df3.style.apply(highlight_diff,threshold=1.0,column=df3.columns, axis=1)
        df3_html = df3_style.render(classes="table table-hover table-striped table-sm table-bordered")

        #df4 = df1.merge(df2, how ='outer', left_index=True, right_index=True)
        #df4_html = df4.to_html(classes="table table-hover table-striped table-sm table-bordered")

    return render_template("public/data_preview.html", data_type = data_type, df3 = df3_html, page=page.get_page_number(user))


@users.route("/data_preview_expanded", methods = ["GET", "POST"])
@login_required
def data_preview_expanded():
    user = get_user()
    page = Page()

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
        path = os.path.join(app.config["OBS_FILES_DIR"]) + ("/{}".format(user.username)) + ("/obs")
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

    return render_template("public/data_preview_expanded.html", data_type = data_type, df1 = df1_html, df2 = df2_html, df3 = df3_html, df4 = df4_html, page=page.get_page_number(user))

@users.route("/show_plot", methods = ["GET", "POST"])
@login_required
def show_plot():
    user = get_user()

    # add action to user history
    user_log = UserLog(user.id, "show_plot", datetime.now().replace(microsecond=0))
    user_log.add()

    path = os.path.join(app.config["OBS_FILES_DIR"]) + ("/{}".format(user.username)) + ("/obs")
    html_path = os.path.join(app.config["HTML_FILE_PATH"]) + ("/{}".format(user.username))
    if not os.path.exists(html_path):
        os.makedirs(html_path)
    files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

    if len(files) ==1:
        obs_file_1 = path + '/' + files[0]
        df1 = converttoDF(obs_file_1)
        plot_go(df1,os.path.basename(obs_file_1), html_path)

    elif len(files) == 2:
        obs_file_1 = path + '/' + files[0]
        obs_file_2 = path + '/' + files[1]
        df1 = converttoDF(obs_file_1)
        df2 = converttoDF(obs_file_2)
        df3 = df1.merge(df2, on = 'time', how ='outer')
        plot_go(df3, os.path.basename(obs_file_1) +' and ' + os.path.basename(obs_file_2), html_path)

    return render_template('public/user_html/'+user.username+'/temp-plot.html')

@users.route("/plot")
@login_required
def plot():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "plot", datetime.now().replace(microsecond=0))
    user_log.add()
    page=Page()

    return render_template("public/plot.html", page=page.get_page_number(user))

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
    page = Page()

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

        if request.form['dir'] == 'back':
            return redirect(url_for(page.page_handler('back',user)))
        else:
            return redirect(url_for(page.page_handler('next',user)))

    # add action to user log
    user_log = UserLog(user.id, "checkout", datetime.now().replace(microsecond=0))
    user_log.add()

    return render_template("public/checkout.html", email = user.email if user.email is not None else '', one_sitting = user.one_sitting, task1_like = user.task1_like if user.task1_like is not None else '', task2_like = user.task2_like if user.task2_like is not None else '', page=page.get_page_number(user))

@users.route("/finish")
@login_required
def finish():
    user = get_user()

    # add action to user log
    user_log = UserLog(user.id, "finish", datetime.now().replace(microsecond=0))
    user_log.add()
    page = Page()

    return render_template("public/finish.html", page=page.get_page_number(user))

@users.route("/update_password",methods = ["GET", "POST"])
@login_required
def update_password():

    user = get_user()
    # add action to user history
    user_log = UserLog(user.id, "update_password", datetime.now().replace(microsecond=0))
    user_log.add()

    if request.method == "POST":

        req = request.form
        password = req.get("password")
        re_password = req.get("re_password")
        if password != re_password:
            flash("Passwords don't match","danger")
        else:
            user.update_password(req.get("password"))
            flash("Password updated","success")

    return render_template("public/profile.html")


class Page():
    page_dict_0 = {'signin':['welcome',0,0],
                        'welcome':['consent_form',1,2],
                        'consent_form':['participants_info',2,9],
                        'participants_info':['download',3,18],
                        'download':['crhm',4,30],
                        'crhm':['crhm_guid',5,39.5],
                        'crhm_guid':['crhm_tlx',6,47],
                        'crhm_tlx':['new_intro',7,54.5],
                        'new_intro':['data_preview',8,62],
                        'data_preview':['plot',9,69.5],
                        'plot':['new_tlx',10,77],
                        'new_tlx':['checkout',11,84.5],
                        'checkout':['finish',12,92],
                        'finish':['signout',13,100]}


    page_dict_1 = {'signin':['welcome',0,0],
                        'welcome':['consent_form',1,2],
                        'consent_form':['participants_info',2,9],
                        'participants_info':['new_intro',3,18],
                        'new_intro':['data_preview',4,30],
                        'data_preview':['plot',5,39.5],
                        'plot':['new_tlx',6,47],
                        'new_tlx':['download',7,54.5],
                        'download':['crhm',8,62],
                        'crhm':['crhm_guid',9,70.5],
                        'crhm_guid':['crhm_tlx',10,77],
                        'crhm_tlx':['checkout',11,84.5],
                        'checkout':['finish',12,92],
                        'finish':['signout',13,100]}

    page_dict_webvis = {'signin':['dashboard',0,0]}

    def get_page_number(self, user):
        if user.random_state == '0':
            current_page = os.path.basename(request.path)
            return self.page_dict_0.get(current_page)[1:]
        elif user.random_state == '1':
            current_page = os.path.basename(request.path)
            return self.page_dict_1.get(current_page)[1:]
        else:
            current_page = os.path.basename(request.path)
            return self.page_dict_webvis.get(current_page)[1:]



    def page_handler(self,direction,user):
        current_page = os.path.basename(request.path)

        def get_key(val, my_dict):
            for key, value in my_dict.items():
                if val == value[0]:
                    return key
        next_page = ''
        pre_page = ''

        if user.random_state == '0':
            next_page = self.page_dict_0.get(current_page)[0]
            pre_page = get_key(current_page, self.page_dict_0)
        else:
            next_page = self.page_dict_1.get(current_page)[0]
            pre_page = get_key(current_page, self.page_dict_1)

        if direction == 'next':
            return 'users.'+next_page
        else:
            return 'users.'+pre_page


