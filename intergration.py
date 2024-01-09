import ses
import json
import boto3
from botocore.exceptions import ClientError


def ses_send(content, recipients, is_monthly):
    if is_monthly:
        word = '[Monthly]'
    else:
        word = '[Daily]'
    sender = "dev2@useb.co.kr"
    recipient = recipients
    subject = f"{word} Face Server API Usage"
    body_text = str(content)
    body_html = str(content)
    ses.send(sender, recipient, subject, body_text, body_html)


def get_secrets(secret_name, output: str = 'json'):
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
