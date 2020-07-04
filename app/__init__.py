from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
if app.config["ENV"] == 'development':
    app.config.from_object("config.DevelopmentConfig")
elif app.config["ENV"] == 'production':
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV"] == 'testing':
    app.config.from_object("config.TestingConfig")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'
login_manager.login_message_category = 'info'

from app import views
from app import admin_views