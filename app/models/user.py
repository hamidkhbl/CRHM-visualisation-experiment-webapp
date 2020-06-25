from flask_sqlalchemy import SQLAlchemy
import sys
sys.path.append("../")
from app import app
import os
from passlib.hash import sha256_crypt
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

db = SQLAlchemy(app)
file_path = os.path.abspath(os.getcwd())+"\data/crhm.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

class User(db.Model):
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

    def get_user_by_secret_key(self, secret_key):
        return User.query.filter_by(secret_key = secret_key).first()

    def update_last_time_loggedin(self, time):
        self.last_time_loggedin = time
        db.session.commit()


    def update_password(self, new_password):
        self.password = sha256_crypt.encrypt(new_password)
        db.session.add(self)
        db.session.commit()

    def update_userInfo(self, age, crhm_exp, gender, dev_exp_years, test_exp_years, role_exp):
        self.age = age
        self.crhm_exp = crhm_exp
        self.gender = gender
        self.dev_exp_years = dev_exp_years
        self.test_exp_years = test_exp_years
        self.role_exp = role_exp
        db.session.commit()

    def update_userEmail(self, email):
        self.email = email
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

    def __init__(self, user_Id, page, mental_demanding, physically_demanding, hurried_rushed, successful_accomplishing, hard_performance, insecure_discouraged):
        self.userId = user_Id
        self.page = page
        self.mental_demanding = mental_demanding
        self.physically_demanding = physically_demanding
        self.hurried_rushed = hurried_rushed
        self.successful_accomplishing = successful_accomplishing
        self.hard_performance = hard_performance
        self.insecure_discouraged = insecure_discouraged

    def __repr__(self):
        return f"user({self.userId},{self.page}"

    def add(self):
        db.session.add(self)
        db.session.commit()


db.create_all()
db.session.commit()
