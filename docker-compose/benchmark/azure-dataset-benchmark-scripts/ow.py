import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import requests as requests

ip_address = '146.193.41.200'
url = f'https://{ip_address}/api/v1/namespaces/_/actions/%s?blocking=true&result=false'
headers = {
    "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=",
    "Content-Type": "application/json",
    "User-Agent": "OpenWhisk-CLI/1.0 (2019-08-10T00:47:48.313+0000) linux amd64"
}
registry = CollectorRegistry()
exec_duration = Gauge('function_execution_time', 'Execution time', registry=registry)
cs = Gauge('cold_start_time', 'Cold start time', registry=registry)


def send(function_name, payload):
    request_url = url % function_name
    r = requests.post(request_url, data=json.dumps(payload), headers=headers, verify=False)
    json_response = r.json()
    annotations = json_response['annotations']
    wait_time = 0
    init_time = None
    duration = json_response['duration']

    for a in annotations:
        if a['key'] == 'waitTime':
            wait_time = a['value']

        if a['key'] == 'initTime':
            init_time = a['value']

    total_time = wait_time + (init_time if init_time is not None else 0) + duration
    if init_time is not None:
        cs.set(init_time)
    exec_duration.set(total_time)

    push_to_gateway('146.193.41.231:9092', job=function_name, registry=registry)
