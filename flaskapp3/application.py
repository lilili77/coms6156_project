from flask import Flask
import os
import json

from db import DButil
import boto3
import base64
from botocore.exceptions import ClientError

application = Flask(__name__)


@application.route('/')
def home():
    print("home",get_secret())
    db = DButil(json.loads(get_secret()))
    db.close()
    return f"<p>EB!{get_secret()}</p>"

def get_secret():
    secret_name = os.environ.get('DBSECRET', "")
    region_name = "us-east-1"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print("get secret error",e)
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        # else:
        #     secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return secret


if __name__ == "__main__":
    # for key,val in os.environ.items():
    #     print(f"{key}------{val}")
    # port = int(os.environ.get('PORT', 80))
    print("mmain",get_secret())
    application.run(debug=True, host='0.0.0.0', port=80)