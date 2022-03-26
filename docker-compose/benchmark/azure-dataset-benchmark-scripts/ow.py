import json

import requests as requests

ip_address = '146.193.41.200'
url = f'https://{ip_address}/api/v1/namespaces/_/actions/%s?blocking=true&result=true'
headers = {
    "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=",
    "Content-Type": "application/json",
    "User-Agent": "OpenWhisk-CLI/1.0 (2019-08-10T00:47:48.313+0000) linux amd64"
}


def send(function_name, payload):
    request_url = url % function_name
    r = requests.post(request_url, data=json.dumps(payload), headers=headers, verify=False)
    print(r)
