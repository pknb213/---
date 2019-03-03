from flask import Flask
import os
import flask_login

UPLOAD_FOLDER = './FlaskServer/static/excel'
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import FlaskServer.views

################################################################################


