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
    username = db.Column(db.String(20), nullable = True)
    password = db.Column(db.String(20), nullable = True)
    last_time_loggedin = db.Column(db.String(20))

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

db.create_all()
db.session.commit()