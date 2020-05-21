from flask_sqlalchemy import SQLAlchemy
import sys
sys.path.append("../")
from app import app
import os


db = SQLAlchemy(app)
file_path = os.path.abspath(os.getcwd())+"\data/crhm.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    last_time_loggedin = db.Column(db.String(20))
    role =  db.Column(db.String(20), nullable = False)
    secret_key = db.Column(db.String(20), default = False)

    def __repr__(self):
        return f"user({self.username},{self.last_time_loggedin})"

    def add(self):
        db.session.add(self)
        db.session.commit()

    def check_password(self, username, password):
        try:
            result = User.query.filter_by(username = username).first().password
        except:
            return False

        if password == result:
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

db.create_all()
db.session.commit()