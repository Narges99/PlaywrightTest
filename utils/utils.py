import requests
import os
import json
from datetime import datetime


def read_test_status(path):
    if os.path.exists(path):
        with open(path, "r") as file:
            return json.load(file)
    else:
        return {}

def update_test_status(test_name, has_error, path):
    status = read_test_status(path)

    if test_name in status:
        if has_error:
            status[test_name] += 1
        else:
            status[test_name] = 0  # reset error count if no error
    else:
        status[test_name] = 1 if has_error else 0  # first time test, set error count

    with open(path, "w") as file:
        json.dump(status, file)

def send_sms(content, destination):
    originator = "50004698986599"
    username = "989124082158"
    password = "Uq142685"
    url = f"https://negar.armaghan.net/sms/url_send.html?originator={originator}&destination={destination}&content={content}&username={username}&password={password}"
    response = requests.get(url)
    return response

def send_sms2(template, parameters, destination):
    data = {
        "username": "989124082158",
        "password": "Uq142685",
        "template": template,
        "parameters": parameters,
        "destinations": [destination]
    }

    url = "https://negar.armaghan.net/webservice/rest/sendParameterizedMessage"
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Message sent successfully:", response.json())
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def is_valid_time():
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    return current_hour in [6, 9, 12, 15] and current_minute < 10