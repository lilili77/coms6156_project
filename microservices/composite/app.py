from flask import Flask
import os
import json

import requests
from datetime import datetime

# This app is deployed in EC2
# Log group for this instance is at  in CloudWatch
app = Flask(__name__)


# Health check
@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"


@app.route('/cp')
def cp():
    url = "https://33j09lwpf9.execute-api.us-east-1.amazonaws.com/prod/" + "user/users"
    username = str(datetime.now().timestamp())
    r = requests.request("POST",
                         url,
                         json={
                             'username': username,
                             'email': 'test@test.com'
                         })
    print(r.json())
    r = requests.request("GET", url)
    return r.json()


if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)