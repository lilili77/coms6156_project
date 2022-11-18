from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

sa = SQLAlchemy()
ma = Marshmallow()


class UserModel(sa.Model):
    __tablename__ = 'users'
    username = sa.Column(sa.String,
                         primary_key=True,
                         unique=True,
                         nullable=False)
    email = sa.Column(sa.String)
    current_room_id = sa.Column(sa.Integer, nullable=True)


class UserSchema(ma.Schema):
    username = fields.String()
    email = fields.String()
    current_room_id = fields.Integer()
