from flask import Flask
import os
import json

from db import DButil

app = Flask(__name__)


@app.route('/fargate/dbtest')
def dbtest():
    db = DButil()
    db.close()
    dbhost = json.loads(os.environ.get('dbsecret',"{}"))
    return f"<p>DB host: {dbhost.get('host','Not Found')}</p>"

@app.route('/fargate')
def fargate():
    return f"<p>Fargate routing success</p>"

@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"

if __name__ == "__main__":
    for key,val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)