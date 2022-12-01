from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

sa = SQLAlchemy()
ma = Marshmallow()


class VideoModel(sa.Model):
    __tablename__ = 'video'
    id = sa.Column(sa.Integer, primary_key=True)
    video_url = sa.Column(sa.String(500))
    image_url = sa.Column(sa.String(500))
    name = sa.Column(sa.String(80))
    actor = sa.Column(sa.String(200))
    length = sa.Column(sa.String(200))
    genre = sa.Column(sa.String(80))
    review_rating = sa.Column(sa.Float)

    def __init__(self, video_url, name, actor, length, genre, review_rating, image_url):
        self.video_url = video_url
        self.name = name
        self.actor = actor
        self.length = length
        self.genre = genre
        self.review_rating = review_rating
        self.image_url = image_url


class VideoSchema(ma.Schema):
    id = fields.Integer()
    name = fields.String(required=True)
    video_url = fields.String(required=True)
    actor = fields.String(required=False)
    length = fields.String(required=True)
    genre = fields.String(required=False)
    review_rating = fields.Float(required=False)
    image_url = fields.String(required=False)