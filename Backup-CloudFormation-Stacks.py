import boto3
import os
import json

cf= boto3.client('cloudformation')
s3 = boto3.client('s3')
sts_client = boto3.client('sts')

def lambda_handler(event, context):
    stacks = cf.describe_stacks()
    customer = os.getenv('CUSTOMER')
    account_id = sts_client.get_caller_identity()["Account"]
    for stack in stacks['Stacks']:
        stack_name = stack['StackName']
        template_body = cf.get_template(StackName=stack_name)['TemplateBody']
        folder_name = f"{customer}/{account_id}/CloudFormation/"
        backup_name = f"{folder_name}{stack_name}/template-backup.json"
        bucket_name = os.getenv('BUCKET')
        s3.put_object(Body=json.dumps(template_body), Bucket=bucket_name, Key=backup_name)
