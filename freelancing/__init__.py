from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
import os
import certifi


ca = certifi.where()

freelancing = Flask(__name__, template_folder='views', static_folder='static')
UPLOAD_FOLDER = os.path.join(freelancing.root_path, 'static', 'uploads')  # Use os.path.join to get the absolute path
freelancing.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure MongoDB URI and JWT
freelancing.config["MONGO_URI"] = "mongodb+srv://axk68420:JGWE4RdbICzCBjNV@cluster0.x6ffwl7.mongodb.net/render-freelancing_store"
freelancing.secret_key = 'freelancing'


mongo = PyMongo(freelancing, tlsCAFile=ca)

jwt = JWTManager(freelancing)

