from db import DButil
from flask import Flask
import os
import json

import sys
# db util class is imported from ../room/db.py
# Add path to the sys.path so that we can import it
db_dir = os.path.join(os.path.dirname(__file__), '..', 'room')
sys.path.append(db_dir)


# This app is deployed in Fargate
# Log group for this instance is at COMS6156ProjectStack-FargateCustomLogGroup{some id} in CloudWatch
app = Flask(__name__)


# Health check
@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"


@app.route('/user')
def fargate():
    return f"<p>route:/user instance:Fargate</p>"


@app.route('/user/dbtest')
def dbtest():
    db = DButil()
    db.close()
    dbhost = json.loads(os.environ.get('dbsecret', "{}"))
    return f"<p>route:/user/dbtest instance:Fargate</p> <br> <p>DB host: {dbhost.get('host','Not Found')}</p>"


if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)
