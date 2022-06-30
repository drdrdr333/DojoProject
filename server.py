from distutils.log import debug
from flask_app.controllers import controller_user
from flask_app import app


if __name__ == '__main__':
    app.run(debug=True)