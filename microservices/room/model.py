from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

db = SQLAlchemy()
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