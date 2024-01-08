import requests
import json


def send(webhook_url, message):
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
