##CSRF enabled to stop cross site scripting
WTF_CSRF_ENABLED = True
SECRET_KEY = 'a-very-secret-stationary-secret'

##define location of database
import os
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True 