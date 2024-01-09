import boto3
import time
from datetime import datetime, timedelta

import log_insight
import intergration
import converter
import slack

# log_group = '/aws/apigateway/log-prd-faceserver-httpapi'
log_group = '/aws/apigateway/fs-java-logs'
user_pool_id = 'ap-northeast-2_lfp7T7azV'


def get_fs_usage_count(standard_date, start_time, end_time):
    client = boto3.client('logs')

    usage = []
    for app_client in get_app_client_ids():
        query = log_insight.query_count(app_client, start_time, end_time)

        try:
            query_id = client.start_query(
                logGroupName=log_group,
                # startTime=int(start_time.timestamp()),
                startTime=1701408610000,
                endTime=int(end_time.timestamp()),
                queryString=query
            )['queryId']
            response = None
            while response is None or response['status'] == 'Running':
                time.sleep(1)
                response = client.get_query_results(queryId=query_id)

            result_count = response['results'][0][0]['value'] if response['results'] else 0
        except Exception as e:
            print(f"Error during query for client {app_client['ClientId']}: {e}")

        usage.append({
            'StandardDate': standard_date,
            'ClientName': app_client["ClientName"],
            'Count': result_count
        })

    return usage


def get_fs_usage_raw(standard_date, start_time, end_time):
    client = boto3.client('logs')

    for app_client in get_app_client_ids():
        query = log_insight.query_raw(app_client, start_time, end_time)
        print(f'## app client: {app_client}')

        # Get Query ID
        try:
            query_id = client.start_query(
                logGroupName=log_group,
                # startTime=int(start_time.timestamp()),
                startTime=1701408610000,
                endTime=int(end_time.timestamp()),
                queryString=query
            )['queryId']

            # Execute Query && Wait for the query to be done
            response = None
            while response is None or response['status'] == 'Running':
                time.sleep(1)
                response = client.get_query_results(queryId=query_id)
                # print(response)

            # Check if result exists (Which means, the app has request logs)
            if response['results'][0]:
                result_raw = converter.create_csv(response)
                print(result_raw)

        except Exception as e:
            print(f"Error during query for client {app_client['ClientId']}: {e}")

    return result_raw


def get_app_client_ids():
    try:
        client = boto3.client('cognito-idp')

        response = client.list_user_pool_clients(UserPoolId=user_pool_id)
        app_clients = response.get('UserPoolClients', [])

        client_info = []
        for client in app_clients:
            client_info.append({
                'ClientName': client['ClientName'],
                'ClientId': client['ClientId']
            })
        return client_info
    except Exception as e:
        print(f"Error: {e}")
        return None


def set_monthly():
    now = datetime.now()
    first_day_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_time = first_day_of_current_month - timedelta(days=1) + timedelta(hours=23, minutes=59, seconds=59,
                                                                          microseconds=999999)
    start_time = end_time.replace(day=1)
    standard_date = start_time.date().strftime('[Monthly] %Y년 %m월')
    return standard_date, start_time, end_time


def set_daily():
    end_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=1)
    standard_date = start_time.date().strftime('[Daily] %Y년 %m월 %d일')
    return standard_date, start_time, end_time


def lambda_handler(event, context):
    is_monthly = event.get('monthly', False)
    webhook_url = intergration.get_secrets(secret_name="slack-webhookURL-yk.kwon-alchera")[
        'SLACK_WEBHOOK_URL_common-notify']
    token = intergration.get_secrets(secret_name="slack-webhookURL-yk.kwon-alchera")[
        'SLACK_TOKEN_fileUpload']
    channel_id = intergration.get_secrets(secret_name="slack-webhookURL-yk.kwon-alchera")[
        'SLACK_CHANNEL_ID']

    if is_monthly:  # monthly usage (Payload comes from Amazon EventBridge Scheduler)
        standard_date, start_time, end_time = set_monthly()
        fs_usage_raw = get_fs_usage_raw(standard_date, start_time, end_time)

        file_path = 'usage.csv'
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            file.write(fs_usage_raw)

        slack.api_fileUpload(token=token, file=file_path, channel_id=channel_id)
    elif not is_monthly:  # daily usage
        standard_date, start_time, end_time = set_daily()
        fs_usage_raw = get_fs_usage_raw(standard_date, start_time, end_time)

        file_path = 'usage.csv'
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            file.write(fs_usage_raw)

        slack.webhook_send(message=fs_usage_raw, webhook_url=webhook_url)
    # Send SES
    # recipients = ["yk.kwon@alcherainc.com", "dh.yang@alcherainc.com", "chssha98@useb.co.kr"]
    # intergration.send_ses(content=converter.list_to_html(usage), recipients=recipients, is_monthly=is_monthly)


if __name__ == '__main__':
    aws_account_id = '260923642723'
    lambda_name = 'lambda-faceserver-apiMonitor'
    event_dict = {}
    context_dict = {
        'log_group_name': f'/aws/lambda/{lambda_name}',
        'function_name': {lambda_name},
        'memory_limit_in_mb': 128,
        'function_version': '$LATEST',
        'invoked_function_arn': f'arn:aws:lambda:ap-northeast-2:{aws_account_id}:function:{lambda_name}',
        'client_context': None,
        'identity': {
            'cognito_identity_id': None,
            'cognito_identity_pool_id': None
        }
    }

    lambda_handler(event_dict, context_dict)
