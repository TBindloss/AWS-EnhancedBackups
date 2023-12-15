import boto3
import os
import urllib.request
import tempfile
import json

def lambda_handler(event, context):
    lambda_client = boto3.client('lambda')
    s3_client = boto3.client('s3')
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]
    customer = os.getenv('CUSTOMER')
    functions = lambda_client.list_functions()
    bucket_name = os.getenv('BUCKET')
    for function in functions['Functions']:
        function_name = function['FunctionName']
        function_details = lambda_client.get_function(FunctionName=function_name)
        runtime = function_details['Configuration']['Runtime']
        role = function_details['Configuration']['Role']
        timeout = function_details['Configuration']['Timeout']
        memorysize = function_details['Configuration']['MemorySize']
        architecture = function_details['Configuration']['Architectures']
        code_location = function_details['Code']['Location']
        response = urllib.request.urlopen(code_location)
        code = response.read()
        temp_dir = tempfile.mkdtemp()
        with open(os.path.join(temp_dir, 'function.zip'), 'wb') as code_file:
            code_file.write(code)
        function_info = {
            'FunctionName': function_name,
            'Runtime': runtime,
            'Role': role,
            'Timeout': timeout,
            'Memory Size' : memorysize,
            'Architecture' : architecture
        }
        config_file_path = os.path.join(temp_dir, 'function_config.json')
        with open(config_file_path, 'w') as config_file:
            json.dump(function_info, config_file, default=str)
        s3_code_key = f'{customer}/{account_id}/Lambdas/{function_name}/function.zip'
        s3_client.upload_file(os.path.join(temp_dir, 'function.zip'), bucket_name, s3_code_key)
        s3_config_key = f'{customer}/{account_id}/Lambdas/{function_name}/function_config.json'
        s3_client.upload_file(config_file_path, bucket_name, s3_config_key)
        os.remove(os.path.join(temp_dir, 'function.zip'))
        os.remove(config_file_path)
        os.rmdir(temp_dir)