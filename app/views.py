from app import app
from flask import Flask, request, redirect, render_template, flash, url_for, session
import sys
sys.path.append('app/models')
from user import User
from datetime import datetime

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
            user.update_last_time_loggedin(datetime.now().replace(microsecond=0))
            session["SECRETKEY"] = user.secret_key
            flash("Signed in","success")
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

    return render_template("public/welcome.html", username = user.username)

@app.route("/signout")
def signout():
    session.pop("SECRETKEY", None)
    return redirect(url_for("signin"))

@app.route("/profile")
def profile():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))
    return render_template("public/profile.html", user = user)

@app.route("/download")
def download():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))
    return render_template("public/download.htm", username = user.username)

@app.route("/upload")
def upload():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))
    return render_template("public/upload.html", username = user.username)

@app.route("/crhm")
def crhm():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))
    return render_template("public/crhm.html", username = user.username)

@app.route("/data_preview")
def data_preview():
    user = get_user()
    if user is None:
        return redirect(url_for("signin"))
    return render_template("public/data_preview.html", username = user.username)