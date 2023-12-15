import boto3
import json
import os

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    s3_client = boto3.client('s3')
    sts_client = boto3.client('sts')
    response = ec2_client.describe_security_groups()
    account_id = sts_client.get_caller_identity()["Account"]
    customer = os.getenv('CUSTOMER')
    for security_group in response['SecurityGroups']:
        security_group_id = security_group['GroupId']
        security_group_name = security_group['GroupName']
        sg_data = {
            'SecurityGroupName': security_group_name,
            'SecurityGroupId': security_group_id,
            'VPC': security_group['VpcId'],
            'InboundRules': security_group['IpPermissions'],
            'OutboundRules': security_group['IpPermissionsEgress']
        }

        json_data = json.dumps(sg_data, indent=4)
        folder_name = f'{customer}/{account_id}/SecurityGroups/{security_group_id}/'        
        bucket_name = os.getenv('BUCKET')
        file_name = f'{folder_name}{security_group_name}-config.json'
        s3_client.put_object(Body=json_data, Bucket=bucket_name, Key=file_name)

