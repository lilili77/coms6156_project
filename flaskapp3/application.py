from flask import Flask
import os
import json

from db import DButil

application = Flask(__name__)


# @app.route('/fargate/dbtest')
# def dbtest():
#     db = DButil()
#     db.close()
#     dbhost = json.loads(os.environ.get('dbsecret',"{}"))
#     return f"<p>DB host: {dbhost.get('host','Not Found')}</p>"

# @app.route('/eb')
# def fargate():
#     return f"<p>Fargate routing success</p>"

@application.route('/')
def home():
    return "<p>EB!</p>"

if __name__ == "__main__":
    # for key,val in os.environ.items():
    #     print(f"{key}------{val}")
    # port = int(os.environ.get('PORT', 80))
    application.run(debug=True, host='0.0.0.0', port=80)