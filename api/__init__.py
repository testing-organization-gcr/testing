from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
application = Flask(__name__)
CORS(application)
from api import routes
from api import database
from api.database import db


# from backend.app.api.database import db
