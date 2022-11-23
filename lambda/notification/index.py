import boto3
import json


# Log group for this instance is at /aws/lambda/COMS6156ProjectStack-NotificationFunction in CloudWatch
def handler(event, context):
    print(event)
    print(context)
    return {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')}
