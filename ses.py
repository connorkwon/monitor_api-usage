import boto3
from botocore.exceptions import ClientError


def send(sender, recipient, subject, body_text, body_html):
    client = boto3.client('ses')

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': recipient,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None
    else:
        return response['MessageId']


