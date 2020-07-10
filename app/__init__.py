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
login_manager.login_view = 'users.signin'
login_manager.login_message_category = 'info'

from app.views import users
from app.admin_views import admin

app.register_blueprint(users, url_prefix='/visualization')
app.register_blueprint(admin, url_prefix='/visualization/admin')