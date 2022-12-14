from flask import Flask, request
import os
import json

import requests
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# This app is deployed in EC2
# Log group for this instance is at COMS6156ProjectStack-CompositeEC2CustomLogGroup in CloudWatch
app = Flask(__name__)


# Health check
@app.route('/')
def home():
    return "<p>Docker Flask App: Hello, World!</p>"


@app.route('/room-user')
def room_user_home():
    return "<p>Docker Flask App: Hello, World!</p>"

#create a room and update user with current_room id
@app.route('/room-user/create_room', methods = ['POST','PUT','GET'])
def create_room_user():
    url_room = os.environ['ApiURL'] + "room/room"
    headers = requests.utils.default_headers()
    json_data_room = request.json
    user_id =json_data_room['host_id']
    response_room = requests.post(url_room, headers=headers, data=json.dumps(json_data_room))
    res = response_room.json()
    url_user = os.environ['ApiURL'] + "user/users/" + str(user_id)
    room_id = { 'current_room_id' :  res['data']['id']  }
    response_user = requests.put(url_user, headers=headers, data=json.dumps(room_id))
    return response_user.text



@app.route('/room-user/detele_room/<int:room_id>', methods = ['PUT','DELETE'])
def delete_room(room_id):
    url_room = os.environ['ApiURL'] + "room/room/" + str(room_id)
    json_data_room = request.json
    headers = requests.utils.default_headers()
    response_room = requests.delete(url_room, headers=headers, data=json.dumps(json_data_room))
    url_user = os.environ['ApiURL'] + "user/remove_users/" + str(room_id)
    response_user = requests.put(url_user, headers=headers)
    return response_room.text + response_user.text



@app.route('/room-user/join_room/<int:user_id>', methods = ['POST','PUT'])
def join_room(user_id):
    url_user = os.environ['ApiURL'] + "user/users/" + str(user_id)
    json_data = request.json
    room_id = { 'current_room_id' :  json_data['current_room_id'] }
    headers = requests.utils.default_headers()
    response_user = requests.put(url_user, headers=headers, data=json.dumps(room_id))
    return response_user.text



@app.route('/room-user/leave_room/<int:user_id>', methods = ['POST','PUT'])
def leave_room(user_id):
    url_user = os.environ['ApiURL'] + "user/users/" + str(user_id)
    room_id = { 'current_room_id' :  None}
    headers = requests.utils.default_headers()
    response_user = requests.put(url_user, headers=headers, data=json.dumps(room_id))
    return response_user.text


@app.route('/room-user/get_all_user/<int:current_room_id>', methods = ['GET'])
def get_users_from_room(current_room_id):
    url_user = os.environ['ApiURL'] + "user/get_users/" + str(current_room_id)
    headers = requests.utils.default_headers()
    response_user = requests.get(url_user, headers=headers)
    return response_user.text


@app.route('/room-user/invite/<int:host_id>/<int:guest_id>/<int:room_id>', methods=['GET')
def sns_test():
    # get invitation link?
    invite_url = os.enviton['ApiURL']'/room-user/join_room/<int:user_id>'
    # get host username
    host_url = os.environ['ApiURL'] + "/user/users/" + str(host_id)
    headers = requests.utils.default_headers()
    response_host = requests.get(host_url, headers=headers).json()
    host_username = response_host['data']['username']
    # get guest username and email
    guest_url = os.environ['ApiURL'] + "/user/users/" + str(guest_id)
    headers = requests.utils.default_headers()
    response_guest = requests.get(guest_url, headers=headers).json()
    guest_username = response_guest['data']['username']
    guest_email = response_guest['data']['email']
    # generate email
    message = "Hi"+ guest_username + "!" + host_username + "is inviting you to watch a video on Zoomflex! The room id is " + str(room_id)
    publishobject = {'Message': message,
                     'Invitationlink': invite_url
                    }
    # Add sns subscriber                
    # client.subscribe(
    #     TopicArn = os.environ['TopicARN'],
    #     Protocal='sns',
    #     Endpoint = email
    # )
    # publish a email
    sns_client = boto3.client('sns', region_name='us-east-1')
    r = sns_client.publish(TopicArn=os.environ['TopicARN'],
                           Message=json.dumps(publishobject),
                           Subject="Invitation to join Zoomflex room")
    return r




if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)