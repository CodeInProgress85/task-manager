from flask import Flask, redirect, flash, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()
    
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["DEBUG"] = os.getenv("DEBUG", "False") == "True"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

login.login_view = "login"

@login.unauthorized_handler
def unauthorized():
    return redirect(url_for('login', next=request.url))

from app import routes, models
