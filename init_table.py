import boto3
from botocore.exceptions import ClientError

def init_table(table_name):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        return table
    except ClientError as e:
        print(f"Error in init table {e}")
        return None