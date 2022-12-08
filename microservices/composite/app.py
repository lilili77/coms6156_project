from flask import Flask
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
def cp():
    return "<p>Room user</p>"


@app.route('/room-user/sns')
def sns_test():
    sns_client = boto3.client('sns', region_name='us-east-1')
    r = sns_client.publish(TopicArn=os.environ['TopicARN'],
                           Message=json.dumps({'test': 'test'}),
                           Subject="Something happend")
    return r

@app.route('/room-user/ses')
def ses():
    
    SENDER = "zoomflex6156@gmail.com" 
    RECIPIENT = "zoomflex6156@gmail.com" # must be verified in AWS SES Email

    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = "This is test email for testing purpose..!!"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("You are invited to a room in zoomflex."
                ""
                )
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1>Hey Hi...</h1>
    <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES CQPOCS</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
        AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>
                """            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
        
                        'Data': BODY_HTML
                    },
                    'Text': {
        
                        'Data': BODY_TEXT
                    },
                },
                'Subject': {

                    'Data': SUBJECT
                },
            },
            Source=SENDER
        )
    
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        


if __name__ == "__main__":
    for key, val in os.environ.items():
        print(f"{key}------{val}")
    port = int(os.environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)