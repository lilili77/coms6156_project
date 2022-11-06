from flask import Flask
import os
import json

import sys
# db util class is imported from ../room/db.py
# Add path to the sys.path so that we can import it
db_dir = os.path.join(os.path.dirname(__file__), '..', 'room')
sys.path.append(db_dir)

from db import DButil

# This app is deployed in EC2
# Log group for this instance is at COMS6156ProjectStack-EC2CustomLogGroup{some id} in CloudWatch
app = Flask(__name__)


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


if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)