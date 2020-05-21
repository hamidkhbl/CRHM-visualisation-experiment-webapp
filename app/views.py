from app import app
from flask import Flask, request, redirect, render_template, flash, url_for
import sys
sys.path.append('app/models')
from user import User

@app.route("/", methods = ["GET", "POST"])
@app.route("/signin", methods = ["GET", "POST"])
def signin():

    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")
        print(username, password)

        user = User()

        if user.check_password(username, password):
            flash("Signed in","success")
            return redirect(url_for("welcome"))
        else:
            flash("Wrong credentials","danger")

    return render_template("public/signin.html")

@app.route("/welcome")
def welcome():
    return render_template("public/welcome.html")