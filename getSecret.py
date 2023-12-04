import json
import boto3
from botocore.exceptions import ClientError


def get_secrets(secret_name):
    client = boto3.client('secretsmanager')

    try:
        response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = response['SecretString']
    secret_dict = json.loads(secret)
    return secret_dict
