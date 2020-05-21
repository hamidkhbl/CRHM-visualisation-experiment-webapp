from app import app
from flask import Flask, request, redirect, render_template, flash, url_for
import sys
sys.path.append('app/models')
from user import User
import secrets

@app.route("/add_user",methods = ["GET", "POST"])
def add_user():
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
