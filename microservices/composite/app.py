from flask import Flask
import os
import json

import requests
from datetime import datetime
import boto3

# This app is deployed in EC2
# Log group for this instance is at COMS6156ProjectStack-CompositeEC2CustomLogGroup in CloudWatch
app = Flask(__name__)


# Health check
@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"


@app.route('/cp')
def cp():
    url = os.environ['ApiURL'] + "user/users"
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


@app.route('/cp/sns')
def sns_test():
    sns_client = boto3.client('sns', region_name='us-east-1')
    r = sns_client.publish(TopicArn=os.environ['TopicARN'],
                           Message=json.dumps({'test': 'test'}),
                           Subject="Something happend")
    return r


if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)