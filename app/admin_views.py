from app import app
from flask import Flask, request, redirect, render_template, flash, url_for, session, Blueprint
import sys
sys.path.append('app/models')
from user import User, UserLog
import secrets
from flask_login import login_user, current_user, logout_user, login_required

admin = Blueprint('admin', __name__)

@admin.route("/add_user",methods = ["GET", "POST"])
@login_required
def add_user():
    user = get_user()

    if not check_admin():
        return redirect(url_for("users.signin"))


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

@admin.route("/update_password",methods = ["GET", "POST"])
@login_required
def update_password():

    user = get_user()

    if not check_admin():
        return redirect(url_for("users.signin"))


    if request.method == "POST":
        req = request.form
        user = User()
        user = user.get_user(req.get("username"))
        user.update_password(req.get("password"))

    return render_template("admin/update_password.html")

def check_admin():
    if current_user.is_authenticated:
        user = User()
        user = user.get_user(current_user.username)

        if user.role == 'admin':
            return True
        else:
            flash("You need admin access to view the page","danger")
            return False

def get_user():
    if current_user.is_authenticated:
        user = User()
        user = user.get_user(current_user.username)
        return user
    else:
        return None