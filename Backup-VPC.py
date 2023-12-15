import boto3
import json
from datetime import datetime
import os

ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
sts_client = boto3.client('sts')

def default(o):
    if isinstance(o, datetime):
        return o.isoformat()

def lambda_handler(event, context):
    vpcs = ec2_client.describe_vpcs()
    account_id = sts_client.get_caller_identity()["Account"]
    customer = os.getenv('CUSTOMER')
    backup_data = {
        "VPCs": []
    }
    for vpc in vpcs['Vpcs']:
        vpc_id = vpc['VpcId']
        subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
        route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
        nat_gateways = ec2_client.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['NatGateways']
        peering_connections = ec2_client.describe_vpc_peering_connections(Filters=[{'Name': 'requester-vpc-info.vpc-id', 'Values': [vpc_id]}])['VpcPeeringConnections']
        elastic_ips = ec2_client.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])['Addresses']
        vpc_data = {
            "VpcId": vpc_id,
            "Subnets": subnets,
            "RouteTables": route_tables,
            "NatGateways": nat_gateways,
            "PeeringConnections": peering_connections,
            "ElasticIPs": elastic_ips
        }
        backup_data["VPCs"].append(vpc_data)
    json_data = json.dumps(backup_data, default=default)
    folder_name = f'{customer}/{account_id}/VPC/{vpc_id}/'
    bucket_name = os.getenv('BUCKET')
    file_name = f'{folder_name}{vpc_id}-config.json'
    s3_client.put_object(Body=json_data, Bucket=bucket_name, Key=file_name)
