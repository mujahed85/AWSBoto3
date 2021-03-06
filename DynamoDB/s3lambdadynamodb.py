import json
import os
import logging
import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
DB_TABLE_NAME = os.environ.get('DB_TABLE_NAME', 'amazondynamodb-table')

S3_CLIENT = boto3.client('s3')
DYNAMODB_CLIENT = boto3.resource('dynamodb', region_name=AWS_REGION)
DYNAMODB_TABLE = DYNAMODB_CLIENT.Table(DB_TABLE_NAME)

def get_data_from_file(bucket, key):
    '''
    Function reads json file uploaded to S3 bucket
    '''
    response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
    content = response['Body']
    data = json.loads(content.read())
    LOGGER.info('%s/%s file content: %s', bucket, key, data)
    return data

def save_data_to_db(data):
    '''
    Function saves data to DynamoDB table
    '''
    result = DYNAMODB_TABLE.put_item(Item=data)
    return result

def lambda_handler(event, context):
    '''
    Main Lambda function method
    '''
    LOGGER.info('Event structure: %s', event)

    for record in event['Records']:
        s3_bucket = record['s3']['bucket']['name']
        s3_file = record['s3']['object']['key']

        data = get_data_from_file(s3_bucket, s3_file)

        for item in data:
            save_data_to_db(item)

    return {
        'StatusCode': 200,
        'Message': 'SUCCESS'
    }
    # TODO implement
    # return {
    #     'statusCode': 200,
    #     # 'body': json.dumps('***********Welcome to Lambda***********!')
    # }

s3 = boto3.resource('s3')
bucket_name = 'bkt28novmujahed'
bucket_notification = s3.BucketNotification(bucket_name)
response = bucket_notification.put(
    NotificationConfiguration={'LambdaFunctionConfigurations': [
        {
            'LambdaFunctionArn': 'arn:aws:lambda:us-east-1:862140262984:function:fn03decmujahedvv',
            'Events': [
                's3:ObjectCreated:*'
            ]
        }
    ]})