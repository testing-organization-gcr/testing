from api import application, jsonify, request, make_response
from .database import Product, patient_schema, patients_schema, db, ma
from redis import StrictRedis
import hashlib
import json
import schedule
import time


# initializing redis instance
def open_redis_connection():
    return StrictRedis(host='redis', port=6379,
                       charset="utf-8", decode_responses=True)

# Method to calculate hash for all the routes


def calHash(id):
    hash = "id_" + hashlib.md5(str.encode(id)).hexdigest()
    return hash


# Initiate redis connection
redis = open_redis_connection()


def ops_db_update_request():
    print("Received connection request from cronserver")
    print("Initating cron job")
    redis = open_redis_connection()
    print("Available keys in redis are: ", redis.keys())
    redisKeys = redis.keys()
    redisValues = redis.mget(redisKeys)
    """
    Below code will make a batch request to store records from redis cache
    to database i.e. dbsqlite/postgres dependening on the environment(Dev/Prod)
    """
    if len(redisValues) == 0:
        return " "
    else:
        for value in redisValues:
            val = json.loads(value)
            # _tmpdbRecord = {"name": val["name"],
            #                 "location": val["location"],
            #                 "streetname": val["streetname"],
            #                 "status": val["status"]
            #                 }
            new_product = Product(val["id"],
                                  val["name"], val["location"], val["streetname"], val["status"])
            try:
                db.session.add(new_product)
                db.session.commit()
                return patient_schema.jsonify(new_product)
            except Exception:
                return {
                    'msg': str(Exception)
                }


def ops_db_delete_request():
    checkRecord = Product.query.filter_by(id=id).count()
    if checkRecord != 0:
        getRecord = Product.query.get(id)
        db.session.delete(getRecord)
        db.session.commit()
        return jsonify({'msg': 'Patient record deleted'})
    else:
        return jsonify({'msg': 'Patient does not exists'})

# create a patient's record
@application.route('/api/patients', methods=['POST'])
def createPatient():
    """
    Below code will construct a dictonary with recieved variables in request
    and will cache the record into redis memory
    """
    hash = calHash(request.json['name'])
    _tmpDict = {
        "id": hash,
        "name": request.json['name'],
        "location": request.json['location'],
        "streetname": request.json['streetname'],
        "status": request.json['status']
    }
    if redis.exists(hash) == 0:
        print("creating cache entry")
        redis.set(hash, json.dumps(_tmpDict), 120)
        return jsonify(_tmpDict)
    else:
        return jsonify({'name': 'patient already exists'})

# get all records of patients stored in database
@application.route('/api/patients', methods=['GET'])
def getPatients():
    cachedResults = redis.keys()
    if not cachedResults:
        all_Products = Product.query.all()
        result = patients_schema.dump(all_Products)
        for resu in result:
            hash = calHash(resu["name"])
            redis.set(hash, json.dumps(resu), 120)
        return make_response(jsonify(result), 200)
    else:
        return make_response(jsonify(redis.mget(cachedResults)), 202)

# #get only one record, to use it, this feature needs to implemented in frontend first
# @application.route('/api/patients/<int:id>', methods=['GET'])
# def getPatient(id):
#     _Product=Product.query.get(id)
#     return patient_schema.jsonify(_Product)

# update a patient record to use it, this feature needs to implemented in frontend first
# @application.route('/api/patients/<int:id>', methods=['PUT'])
# def updatePatient(id):
#     getRecord=Product.query.get(id)
#     getRecord.name=request.json['name']
#     getRecord.location=request.json['location']
#     getRecord.streetname=request.json['streetname']
#     getRecord.status=request.json['status']
#     db.session.commit()

# delete a patient record
@application.route('/api/patients/<string:record>', methods=['DELETE'])
def deletePatient(record):
    print("Deleting record with name: ", request.json['name'])
    print("Deleting record with name: ", request.json['id'])
    hash = calHash(request.json['name'])
    if redis.exists(hash) == 1:
        redis.delete(hash)
        print("Record deleted")
        return jsonify({'msg': 'Patient Record deleted'})
        ops_db_update_request()
    else:
        return jsonify({'msg': 'Patient does not exists'})


@application.route('/cron', methods=['GET'])
def cronJob():
    response = ops_db_update_request()
    return response

@application.route('/hello', methods=['GET'])
def helloword():
    return "Hello world", 200