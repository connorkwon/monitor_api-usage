import requests
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def webhook_send(webhook_url, message):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "text": message
    }
    print('Slack Message has been sent')
    # print(json.dumps(data))
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    return response


def api_fileUpload(token, file, channel_id):
    client = WebClient(token=token)

    try:
        response = client.files_upload_v2(channel=channel_id, file=file)
        assert response["file"]  # Check if the file has been uploaded
    except SlackApiError as e:
        print(f"Error uploading file: {e}")
