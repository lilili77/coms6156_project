import boto3
import json
from botocore.exceptions import ClientError


# Log group for this instance is at /aws/lambda/COMS6156ProjectStack-NotificationFunction in CloudWatch
def send_email(message,subject,email):
    SENDER = email # must be verified in AWS SES Email
    RECIPIENT = email # must be verified in AWS SES Email
    AWS_REGION = "us-east-1"
    SUBJECT = subject
    BODY_TEXT = message
    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1></h1>
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

def handler(event, context):
    print(event)
    print(context)
    subject = event['Records'][0]['Sns']['Subject']
    message = event['Records'][0]['Sns']['Message']
    parsed_message = json.loads(message)
    content = parsed_message['Content']
    email = parsed_message['Email']
    print(subject)
    print(content)
    print(email)
    send_email(content,subject,email)
    return {'statusCode': 200, 'body': json.dumps('Email sent')}