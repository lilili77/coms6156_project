from flask import Flask, request
from flask_cors import CORS
import os
import json
import sys
import logging
import boto3

# db util class is imported from ../room/db.py
# Add path to the sys.path so that we can import it
db_dir = os.path.join(os.path.dirname(__file__), '..', 'room')
sys.path.append(db_dir)

from db import DButil

# This app is deployed in Fargate
# Log group for this instance is at COMS6156ProjectStack-FargateCustomLogGroup{some id} in CloudWatch
app = Flask(__name__)
CORS(app)
logger = logging.getLogger()

# Cognito
cognito = boto3.client('cognito-idp')


def get_client_id():
    return os.environ.get('cognito_userPoolClientId', '')


def get_user_pool_id():
    return os.environ.get('cognito_userPoolId', '')


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


@app.route('/user/cognito-test')
def cognito_test():
    return {
        'user_pool_id': get_user_pool_id(),
        'user_pool_client_id': get_client_id()
    }, 200


def is_empty(text):
    return text is None or text == ''


@app.route('/user/sign-up', methods=['POST'])
def sign_up():
    json_data = request.get_json(force=True)
    print(json_data)
    username = json_data["username"]
    email = json_data["email"]
    password = json_data["password"]

    if is_empty(username) or is_empty(password) or is_empty(email):
        return {
            'status': 'error',
            'message': 'The username, email, or password is missing'
        }, 400

    try:
        # create user with admin to skip email verification
        response = cognito.admin_create_user(UserPoolId=get_user_pool_id(),
                                             Username=username,
                                             UserAttributes=[{
                                                 'Name': 'email',
                                                 'Value': email
                                             }],
                                             MessageAction='SUPPRESS')

        response = cognito.admin_set_user_password(
            UserPoolId=get_user_pool_id(),
            Username=username,
            Password=password,
            Permanent=True)
    except cognito.exceptions.UsernameExistsException as e:
        return {
            'status': 'error',
            'message': 'This username already exists'
        }, 400
    except cognito.exceptions.InvalidPasswordException as e:
        return {
            'status':
            'error',
            'message':
            'Password should have lowercase, uppercase, special chars, numbers with at least 8 chars.'
        }, 400
    except Exception as e:
        return {'status': False, 'message': str(e)}, 400

    return {'status': 'success', 'message': 'Registered'}, 200


@app.route('/user/sign-in', methods=['POST'])
def sign_in():
    json_data = request.get_json(force=True)
    print(json_data)
    username = json_data["username"]
    password = json_data["password"]

    if is_empty(username) or is_empty(password):
        return {
            'status': 'error',
            'message': 'The username or password is missing'
        }, 400

    try:
        response = cognito.initiate_auth(ClientId=get_client_id(),
                                         AuthFlow='USER_PASSWORD_AUTH',
                                         AuthParameters={
                                             'USERNAME': username,
                                             'PASSWORD': password,
                                         })
    except cognito.exceptions.NotAuthorizedException:
        return {
            'status': 'error',
            'message': 'The username or password is incorrect'
        }, 400
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 400

    auth_result = response['AuthenticationResult']
    return {
        'status': 'success',
        'message': 'Logged in',
        'data': {
            'accessToken': auth_result['AccessToken'],
            'refreshToken': auth_result['RefreshToken'],
            'expiresIn': auth_result['ExpiresIn']
        }
    }, 200


if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)
