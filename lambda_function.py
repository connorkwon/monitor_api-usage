import ses
import slack
import getSecret
import converter
import boto3
import time
from datetime import datetime, timedelta

log_group = '/aws/apigateway/fs-java-logs'
user_pool_id = 'ap-northeast-2_lfp7T7azV'


def fs_usage(start_time, end_time, standard_date):
    client = boto3.client('logs')

    usage = []
    for app_client in get_app_client_ids():
        query = f"""
            fields @timestamp, @message, @logStream, @log, clientId
            | filter clientId = '{app_client['ClientId']}'
            | filter (status = 200) or (status >= 400 and status < 500)
            | filter @timestamp >= {int(start_time.timestamp()) * 1000} and @timestamp < {int(end_time.timestamp()) * 1000}
            | count()
        """
        print(query)

        try:
            query_id = client.start_query(
                logGroupName=log_group,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query
            )['queryId']
            response = None
            while response is None or response['status'] == 'Running':
                time.sleep(1)
                response = client.get_query_results(queryId=query_id)

            count = response['results'][0][0]['value'] if response['results'] else 0
            print('response')
            print(response)
        except Exception as e:
            print(f"Error during query for client {app_client['ClientId']}: {e}")

        usage.append({
            'StandardDate': standard_date,
            'ClientName': app_client["ClientName"],
            'Count': count
        })

    return usage


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


def send_slack(content, webhook_url):
    slack.send(webhook_url=webhook_url, message=content)


def send_ses(content, recipients, is_monthly):
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


def lambda_handler(event, context):
    is_monthly = event.get('monthly', False)
    if is_monthly:  # monthly usage (Payload comes from Amazon EventBridge Scheduler)
        now = datetime.now()
        first_day_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_time = first_day_of_current_month - timedelta(days=1) + timedelta(hours=23, minutes=59, seconds=59,
                                                                              microseconds=999999)
        start_time = end_time.replace(day=1)
        standard_date = start_time.date().strftime('%Y년 %m월')

    elif not is_monthly:  # daily usage
        end_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(days=1)
        standard_date = start_time.date().strftime('%Y년 %m월 %d일')

    # Send Slack
    usage = fs_usage(start_time, end_time, standard_date)
    webhook_url = getSecret.get_secrets(secret_name="slack-webhookURL-yk.kwon-alchera")['SLACK_WEBHOOK_URL']
    send_slack(content=converter.friendly_text(usage), webhook_url=webhook_url)

    # Send SES
    recipients = ["yk.kwon@alcherainc.com", "dh.yang@alcherainc.com"]
    # recipients = ["yk.kwon@alcherainc.com"]
    send_ses(content=converter.list_to_html(usage), recipients=recipients, is_monthly=is_monthly)