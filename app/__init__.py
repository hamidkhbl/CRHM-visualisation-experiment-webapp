from flask import Flask

app = Flask(__name__)
if app.config["ENV"] == 'development':
    app.config.from_object("config.DevelopmentConfig")
elif app.config["ENV"] == 'production':
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV"] == 'testing':
    app.config.from_object("config.TestingConfig")

from app import views
from app import admin_views