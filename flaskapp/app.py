from re import L
from flask import Flask
import os
import json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask import request
from sqlalchemy import create_engine

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://login:password.@127.0.0.1/test'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://login:password.@localhost:8080'
# engine = create_engine("postgresql://postgres:postgres@localhost:8080/test_6156")
db = SQLAlchemy(app)
ma = Marshmallow()

class RoomModel(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer)
    #db.ForeignKey('user.id', ondelete='CASCADE')
    video_id = db.Column(db.Integer)
    name = db.Column(db.String(80))
    #db.ForeignKey('user.id', ondelete='CASCADE')
    def __init__(self, host_id, video_id, name):
        self.host_id = host_id
        self.video_id = video_id
        self.name = name

class RoomSchema(ma.Schema):
    id =  fields.Integer()
    host_id = fields.Integer(required=True)
    video_id = fields.Integer(required=True)
    name = fields.String(required=True)

rooms_schema  = RoomSchema(many=True)
room_schema = RoomSchema()

#initail create for database
with app.app_context(): 
    db.create_all()

@app.route('/room/create', methods = ['POST'])
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
    room = RoomModel(
        host_id=json_data['host_id'],
        video_id=json_data['video_id'],
        name = json_data['name']
    )
    db.session.add(room)
    db.session.commit()

    result = room_schema.dump(room)
    return { "status": 'success', 'data': result }, 201


@app.route('/room/getAll', methods = ['GET'])
def get_all_rooms():
        rooms = RoomModel.query.all()
        rooms = rooms_schema.dump(rooms)
        if not rooms:
            return {'status':'not found'}, 404
        return {'status':'success', 'data':rooms}, 200


@app.route('/room/get/<int:id>', methods = ['GET'])
def get_room(id):
        room = RoomModel.query.get(id)
        print(room)
        room = room_schema.dump(room)
        if not room:
            return {'status':'not found'}, 404
        return {'status':'success', 'data':room}, 200


#only host can delete room
#'<int:host_id>/room/delete/<int:id>'
@app.route('/<int:host_id>/room/delete/<int:id>', methods = ['DELETE'])
def delete_room(host_id, id):
        room = RoomModel.query.get(id)
        if host_id != room.host_id:
            return {'message': 'Action not do valid, host_id not match'}, 400
        room = RoomModel.query.filter_by(id=id).delete()
        db.session.commit()
        result = room_schema.dump(room)
        return { "status": 'success', 'data': result}, 204


#only host can update room
#'<int:host_id>/room/update/<int:id>'
@app.route('/<int:host_id>/room/update/<int:id>', methods = ['PUT'])
def update_room(host_id,id):
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
    room = RoomModel.query.get(id)
    if not room:
        return {'message': 'Room do not exist'}, 400
    if host_id != room.host_id:
        return {'message': 'Action not do valid, host_id not match'}, 400
    if 'video_id' in json_data:
        room.video_id = json_data['video_id']
    if 'name' in json_data:
        room.name = json_data['name']
    db.session.commit()

    result = room_schema.dump(room)
    return { "status": 'success', 'data': result }, 201



@app.route('/dbtest')
def dbtest():
    dbhost = json.loads(os.environ.get('dbsecret',"{}"))
    return f"<p>DB host: {dbhost.get('host','Not Found')}</p>"


@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"


if __name__ == "__main__":
    # port = int(os.environ.get('PORT', 80))
    # localhost port
    port = int(os.environ.get('PORT', 5432))
    app.run(debug=True, host='0.0.0.0', port=port)