import os
import json
import sys
from flask import Flask, request
from flask_cors import CORS
from model import VideoModel, VideoSchema, sa
from imdb_api import ImdbApi

# db util class is imported from ../room/db.py
# Add path to the sys.path so that we can import it
db_dir = os.path.join(os.path.dirname(__file__), '..', 'room')
sys.path.append(db_dir)

from db import DButil

# This app is deployed in EC2
# Log group for this instance is at COMS6156ProjectStack-EC2CustomLogGroup{some id} in CloudWatch
app = Flask(__name__)
CORS(app)

# Database connection
db = DButil()
db.connect()

app.config["SQLALCHEMY_DATABASE_URI"] = db.database_uri
sa.init_app(app)

with app.app_context():
    sa.create_all()

videos_schema = VideoSchema(many=True)
video_schema = VideoSchema()


# Health check
@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"


@app.route('/video')
def ec2():
    return f"<p>route:/video instance:EC2</p>"


@app.route('/video/dbtest')
def dbtest():
    db = DButil()
    db.close()
    dbhost = json.loads(os.environ.get('dbsecret', "{}"))
    return f"<p>route:/video/dbtest instance:EC2</p> <br> <p>DB host: {dbhost.get('host','Not Found')}</p>"


# add a video POST /video
@app.route('/video/videos', methods=['POST'])
def add_video():
    json_data = request.get_json(force=True)
    if not json_data:
        return {'message': "Input is not valid."}, 400
    imbd = ImdbApi()
    res = imbd.search_movie(json_data['name'])
    if not res:
        return {'message': "Video not found."}, 400
    video = VideoModel(name=res['Title'],
                       video_url=json_data['video_url'],
                       image_url=res['Poster'],
                       actor=res['Actors'],
                       length=res['Runtime'],
                       genre=res['Genre'],
                       review_rating=res['imdbRating'])
    sa.session.add(video)
    sa.session.commit()
    result = video_schema.dump(video)
    return {"status": 'success', 'data': result}, 201


# list all videos GET /video
@app.route('/video/videos', methods=['GET'])
def list_all_videos():
    videos = VideoModel.query.all()
    videos = videos_schema.dump(videos)
    if not videos:
        return {'status': 'not found'}, 404
    return {'status': 'success', 'data': videos}, 200


# show video details GET /video/:id
@app.route('/video/videos/<int:id>', methods=['GET'])
def search_video_by_id(id):
    video = VideoModel.query.get(id)
    if not video:
        return {'status': 'Video not found'}, 404
    video = video_schema.dump(video)
    return {'status': 'success', 'data': video}, 200


# delete video DELETE/video/:id
@app.route('/video/videos/<int:id>', methods=["DELETE"])
def delete_video(id):
    video = VideoModel.query.filter_by(id=id).delete()
    if not video:
        return {'status': 'Video not found'}, 404
    sa.session.commit()
    result = video_schema.dump(video)
    return {"status": 'success', 'data': result}, 204


# update video detail PUT/video/:id
@app.route('/video/videos/<int:id>', methods=["PUT"])
def update_video(id):
    json_data = request.get_json(force=True)
    if not json_data:
        return {'message': "Input is not valid."}, 400
    video = VideoModel.query.get(id)
    if not video:
        return {'message': 'Video does not exist'}, 400
    if 'name' in json_data:
        video.name = json_data['name']
    if 'actor' in json_data:
        video.actor = json_data['actor']
    if 'length' in json_data:
        video.length = json_data['length']
    if 'genre' in json_data:
        video.genre = json_data['genre']
    if 'review_rating' in json_data:
        video.review_rating = json_data['review_rating']
    sa.session.commit()
    result = video_schema.dump(video)
    return {"status": 'success', 'data': result}, 201


if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)
