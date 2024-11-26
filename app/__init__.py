from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_babel import Babel
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect 
from datetime import timedelta

## get the session language (for babel/admin)
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

app = Flask(__name__)

## set up admin page for managing database
babel = Babel(app, locale_selector=get_locale)
admin = Admin(app,template_mode='bootstrap4')

app.config.from_object('config')

# Add CSRF protection to the app
csrf = CSRFProtect(app)

## for the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

## for login logic
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."
login_manager.remember_cookie_duration = timedelta(days=1)  # Set cookie lifespan to 1 days

from app import views, models