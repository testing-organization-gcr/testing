from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from api import application
import os
basedir = os.path.abspath(os.path.dirname(__file__))
# database connectivity
# Please set database URI to this 'sqlite:///' + os.path.join(basedir, 'db.sqlite')  'postgres://postgres:postgres@db/postgres' If postgres doesnt work
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize database
db = SQLAlchemy(application)
# inital Marshmallow
ma = Marshmallow(application)

# Class/Model


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(25), unique=True)
    location = db.Column(db.String(15))
    streetname = db.Column(db.String(15))
    status = db.Column(db.String(10))

    def __init__(self, id, name, location, streetname, status):
        self.id = id
        self.name = name
        self.location = location
        self.streetname = streetname
        self.status = status

# Patient Schema


class PatientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'location', 'streetname', 'status')


# initialize the  schema
patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)
