from app import app
from flask import Flask, request, redirect, render_template, flash, url_for, session
import sys
sys.path.append('app/models')
from user import User
import secrets

@app.route("/add_user",methods = ["GET", "POST"])
def add_user():

    if not check_admin():
        return redirect(url_for("signin"))


    if request.method == "POST":
        req = request.form
        admin = req.get("admin")
        role = 'user'
        if admin is not None:
            role = 'admin'
        user = User(
            username = req.get("username"),
            password = req.get("password"),
            role = role,
            secret_key = secrets.token_urlsafe(16)
        )
        user.add()
    return render_template("admin/add_user.html")

@app.route("/update_password",methods = ["GET", "POST"])
def update_password():

    if not check_admin():
        return redirect(url_for("signin"))


    if request.method == "POST":
        req = request.form
        user = User()
        user = user.get_user(req.get("username"))
        user.update_password(req.get("password"))

    return render_template("admin/update_password.html")

def check_admin():
    if session.get("SECRETKEY", None) is not None:
        secret_key = session.get('SECRETKEY')
        user = User()
        user = user.get_user_by_secret_key(secret_key)

        if user.role == 'admin':
            return True
        else:
            flash("You need admin access to view the page","danger")
            return False
