from flask import Flask
import os
import json

from db import DButil
import boto3
import base64
from botocore.exceptions import ClientError

# This app is deployed in Elastic Beanstalk
# Log group for this instance is at /aws/elasticbeanstalk/COMS-MyCf-{some id}/var/log/web.stdout.log in CloudWatch
application = Flask(__name__)


# Get db secret from secret manager
def get_secret():
    secret_name = os.environ.get('DBSECRET', "")
    region_name = "us-east-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager',
                            region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)
    except ClientError as e:
        print("get secret error", e)
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        # else:
        #     secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return secret


# Health check
@application.route('/')
def home():
    return "<p>EB!</p>"


@application.route('/room')
def room():
    return f"<p>route:/room instance:EB</p>"


@application.route('/room/dbtest')
def roomTest():
    db = DButil(json.loads(get_secret()))
    db.close()
    return f"<p>route:/room/dbtest instance:EB</p> <br> <p>DB info: {get_secret()}</p>"


if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0', port=80)