import boto3
import json
import os

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    s3_client = boto3.client('s3')
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]
    customer = os.getenv('CUSTOMER')
    response = ec2_client.describe_network_acls()
    for nacl in response['NetworkAcls']:
        nacl_id = nacl['NetworkAclId']
        inbound_rules = []
        outbound_rules = []
        for entry in nacl['Entries']:
            if entry['Egress']:
                outbound_rules.append(entry)
            else:
                inbound_rules.append(entry)
        nacl_data = {
            'NetworkAclId': nacl_id,
            'SubnetAssociations': nacl['Associations'],
            'InboundRules': inbound_rules,
            'OutboundRules': outbound_rules
        }
        json_data = json.dumps(nacl_data, indent=4)
        folder_name = f'{customer}/{account_id}/NACL/{nacl_id}/'
        bucket_name = os.getenv('BUCKET')
        file_name = f'{folder_name}{nacl_id}-config.json'
        s3_client.put_object(Body=json_data, Bucket=bucket_name, Key=file_name)
