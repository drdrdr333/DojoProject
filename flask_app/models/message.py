import imp
from flask_bcrypt import Bcrypt
from flask_app.models import user
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL

bcrypt = Bcrypt(app)