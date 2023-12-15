import boto3
import json
import os
from datetime import datetime

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")
    
def get_instance_name(instance):
    for tag in instance.get('Tags', []):
        if tag['Key'] == 'Name':
            return tag['Value']
    return 'N/A'

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    sts_client = boto3.client('sts')
    response = ec2_client.describe_instances()
    account_id = sts_client.get_caller_identity()["Account"]
    customer = os.getenv('CUSTOMER')

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance['LaunchTime'] = datetime_handler(instance['LaunchTime'])
            instance_name = get_instance_name(next((instance for reservation in response['Reservations'] for instance in reservation['Instances'] if instance['InstanceId'] == instance_id), {}))
            json_data = json.dumps(instance, indent=4, default=datetime_handler)
            folder_name = f'{customer}/{account_id}/Instances/{instance_name}/'
            s3_client = boto3.client('s3')
            bucket_name = os.getenv('BUCKET')
            file_name = f'{folder_name}{instance_name}-config.json'
            s3_client.put_object(Body=json_data, Bucket=bucket_name, Key=file_name)
    