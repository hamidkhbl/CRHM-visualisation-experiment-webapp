from flask_sqlalchemy import SQLAlchemy
import sys
sys.path.append("../")
from app import app, login_manager, db
import os
from passlib.hash import sha256_crypt
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import UserMixin

db = SQLAlchemy(app)
file_path = os.path.abspath(os.getcwd())+"\data/crhm.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False)
    password = db.Column(db.String(256), nullable = False)
    last_time_loggedin = db.Column(db.String(20))
    role =  db.Column(db.String(20), nullable = False)
    secret_key = db.Column(db.String(20), nullable = False)

    age = db.Column(db.String(20))
    crhm_exp = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    dev_exp_years = db.Column(db.String(30))
    test_exp_years = db.Column(db.String(30))
    role_exp = db.Column(db.String(50))
    email = db.Column(db.String(50))

    one_sitting = db.Column(db.String(20))
    task1_like = db.Column(db.String(500))
    task2_like = db.Column(db.String(500))
    degree = db.Column(db.String(30))

    def __repr__(self):
        return f"user({self.id},{self.username},{self.last_time_loggedin})"

    def add(self):
        self.username = self.username.lower()
        self.password = sha256_crypt.encrypt(self.password)
        db.session.add(self)
        db.session.commit()

    def check_password(self, username, password):
        try:
            result = User.query.filter_by(username = username.lower()).first().password
        except:
            return False

        if sha256_crypt.verify(password, result):
            return True
        else:
            return False

    def check_admin_password(self, password):
        try:
            result = User.query.filter_by(username = 'Hamid').first().password
        except:
            return False

        if password == result:
            return True
        else:
            return False

    def get_user(self, username):
        return User.query.filter_by(username = username).first()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def get_user_by_secret_key(self, secret_key):
        return User.query.filter_by(secret_key = secret_key).first()

    def update_last_time_loggedin(self, time):
        self.last_time_loggedin = time
        db.session.commit()


    def update_password(self, new_password):
        self.password = sha256_crypt.encrypt(new_password)
        db.session.commit()

    def update_userInfo(self, age, crhm_exp, gender, dev_exp_years, test_exp_years, role_exp, degree):
        self.age = age
        self.crhm_exp = crhm_exp
        self.gender = gender
        self.dev_exp_years = dev_exp_years
        self.test_exp_years = test_exp_years
        self.role_exp = role_exp
        self.degree = degree
        db.session.commit()

    def update_user_checkout_Info(self, email, one_sitting, task1_like, task2_like):
        self.email = email
        self.one_sitting = one_sitting
        self.task1_like = task1_like
        self.task2_like = task2_like
        db.session.commit()

class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column(db.Integer, nullable = False)
    page = db.Column(db.String(20), nullable = False)
    time =  db.Column(db.String(20), nullable = False)

    def __init__(self, user_Id, page, time):
        self.userId = user_Id
        self.page = page
        self.time = time

    def __repr__(self):
        return f"user({self.userId},{self.page}, {self.action},{self.time})"

    def add(self):
        db.session.add(self)
        db.session.commit()

class NasaTLX(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column(db.Integer, nullable = False)
    page = db.Column(db.String(20), nullable = False)
    mental_demanding = db.Column(db.String(20), nullable = False)
    physically_demanding =  db.Column(db.String(20), nullable = False)
    hurried_rushed =  db.Column(db.String(20), nullable = False)
    successful_accomplishing =  db.Column(db.String(20), nullable = False)
    hard_performance =  db.Column(db.String(20), nullable = False)
    insecure_discouraged =  db.Column(db.String(20), nullable = False)
    time = db.Column(db.String(20), nullable = False)
    mismatch = db.Column(db.String(20), nullable = False)

    def __init__(self, user_Id, page, mental_demanding, physically_demanding, hurried_rushed, successful_accomplishing, hard_performance, insecure_discouraged, time, mismatch):
        self.userId = user_Id
        self.page = page
        self.mental_demanding = mental_demanding
        self.physically_demanding = physically_demanding
        self.hurried_rushed = hurried_rushed
        self.successful_accomplishing = successful_accomplishing
        self.hard_performance = hard_performance
        self.insecure_discouraged = insecure_discouraged
        self.time = time
        self.mismatch = mismatch

    def __repr__(self):
        return f"user({self.userId},{self.page}"

    def get_user_tlx(userId, page):
        return NasaTLX.query.filter_by(userId = userId).filter_by(page = page).first()

    def add(self):
        db.session.add(self)
        db.session.commit()



    def update_user_tlx(self, mental_demanding, physically_demanding, hurried_rushed, successful_accomplishing, hard_performance, insecure_discouraged, time, mismatch):
        self.mental_demanding = mental_demanding
        self.physically_demanding = physically_demanding
        self.hurried_rushed = hurried_rushed
        self.successful_accomplishing = successful_accomplishing
        self.hard_performance = hard_performance
        self.insecure_discouraged = insecure_discouraged
        self.time = time
        self.mismatch = mismatch
        db.session.commit()


db.create_all()
db.session.commit()
