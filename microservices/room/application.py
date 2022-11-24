from flask import Flask
from flask import request
import os
import json
import sys
from flask_cors import CORS
import boto3
import base64
from botocore.exceptions import ClientError
from db import DButil
# import boto3
import base64
# from botocore.exceptions import ClientError
from model import RoomModel, RoomSchema, db

# db_dir = os.path.join(os.path.dirname(__file__), '..', 'room')
# sys.path.append(db_dir)

# This app is deployed in Elastic Beanstalk
# Log group for this instance is at /aws/elasticbeanstalk/COMS-MyCf-{some id}/var/log/web.stdout.log in CloudWatch
application = Flask(__name__)
CORS(application)


# Get db secret from secret manager
def get_secret():
    secret_name = os.environ.get('DBSECRET', "")
    region_name = "us-east-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager',
                            region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
    except ClientError as e:
        print("get secret error", e)
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        # else:
        #     secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return secret

rds  = DButil(json.loads(get_secret()))
rds.connect()

application.config["SQLALCHEMY_DATABASE_URI"] = rds.database_uri

db.init_app(application)
rooms_schema  = RoomSchema(many=True)
room_schema = RoomSchema()

with application.app_context():
    db.create_all()


# Health check
@application.route('/')
def home():
    return "<p>EB!</p>"


@application.route('/room')
def room():
    return f"<p>route:/room instance:EB</p>"


@application.route('/room/dbtest')
def roomTest():
    db = DButil(json.loads(get_secret()))
    db.close()
    return f"<p>route:/room/dbtest instance:EB</p> <br> <p>DB info: {get_secret()}</p>"



@application.route('/room/room', methods = ['POST'])
def create_room():
    json_data = request.get_json(force=True)
    if not json_data:
        return {'message': 'No input data provided'}, 400
    # data, errors = room_schema.load(json_data)
    # if errors:
    #     return errors, 422
    # room = room.query.filter_by(id=data['']).first()
    # if room:
    #     return {'message': 'room already exists'}, 400
    #except for room_id there is no unique key so no checking
    if 'host_id' not in json_data or 'video_id' not in json_data or 'name' not in json_data:
        return { "message": 'missing data' }, 400
    room = RoomModel(
        host_id=json_data['host_id'],
        video_id=json_data['video_id'],
        name = json_data['name']
    )
    db.session.add(room)
    db.session.commit()

    result = room_schema.dump(room)
    return { "status": 'success', 'data': result }, 201


@application.route('/room/rooms', methods = ['GET'])
def get_all_rooms():
        rooms = RoomModel.query.all()
        rooms = rooms_schema.dump(rooms)
        if not rooms:
            return {'status':'not found'}, 404
        return {'status':'success', 'data':rooms}, 200


@application.route('/room/room/<int:id>', methods = ['GET'])
def get_room(id):
        room = RoomModel.query.get(id)
        print(room)
        room = room_schema.dump(room)
        if not room:
            return {'status':'not found'}, 404
        return {'status':'success', 'data':room}, 200


#only host can delete room
#'<int:host_id>/room/delete/<int:id>'
@application.route('/room/room/<int:id>', methods = ['DELETE'])
def delete_room(id):
        room = RoomModel.query.get(id)
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        host_id = json_data['host_id']
        if host_id != room.host_id:
            return {'message': 'Action not do valid, host_id not match'}, 400
        room = RoomModel.query.filter_by(id=id).delete()
        db.session.commit()
        result = room_schema.dump(room)
        return { "status": 'success', 'data': result}, 204


#only host can update room
#'<int:host_id>/room/update/<int:id>'
@application.route('/room/room/<int:id>', methods = ['PUT'])
def update_room(id):
    json_data = request.get_json(force=True)
    if not json_data:
        return {'message': 'No input data provided'}, 400
    if 'host_id' not in json_data:
        return {'message': 'Action not valid, host_id not found'}, 400
    host_id = json_data['host_id']
    # data, errors = room_schema.load(json_data)
    # if errors:
    #     return errors, 422
    # room = room.query.filter_by(id=data['']).first()
    # if room:
    #     return {'message': 'room already exists'}, 400
    #except for room_id there is no unique key so no checking
    room = RoomModel.query.get(id)
    if not room:
        return {'message': 'Room does not exist'}, 400
    if host_id != room.host_id:
        return {'message': 'Action not valid, host_id not match'}, 400
    if 'video_id' in json_data:
        room.video_id = json_data['video_id']
    if 'name' in json_data:
        room.name = json_data['name']
    db.session.commit()

    result = room_schema.dump(room)
    return { "status": 'success', 'data': result }, 201




if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    application.run(debug=True, host='0.0.0.0', port=port)