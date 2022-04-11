import json
import subprocess

import urllib3
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway
import requests as requests

DOCKER_GRAAL = 'davidfrickert/openwhisk-runtime-nativeimage-basefunction'
DOCKER_OPENJ9 = 'davidfrickert/photon:11'

ip_address = '146.193.41.200'
url = f'https://{ip_address}/api/v1/namespaces/_/actions/%s?blocking=true&result=false'
headers = {
    "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=",
    "Content-Type": "application/json",
    "User-Agent": "OpenWhisk-CLI/1.0 (2019-08-10T00:47:48.313+0000) linux amd64"
}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

global_registry = CollectorRegistry()
cold_start_counter = Counter('cold_start_counter', 'Cold start counter', registry=global_registry)
cs = Gauge('cold_start_time', 'Cold start time', registry=global_registry)
exec_duration = Gauge('function_execution_time', 'Execution time', registry=global_registry)


def create(function_name, concurrency, memory, unique_id, main):
    if main:
        cmd = f'wsk --apihost https://{ip_address} ' \
              f'--auth 23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP ' \
              f'action create -i {function_name}-photon-{unique_id} jars/{function_name}.jar --main {main} --docker {DOCKER_OPENJ9} -c {concurrency} -m {memory}'
    else:
        cmd = f'wsk --apihost https://{ip_address} ' \
              f'--auth 23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP ' \
              f'action create -i {function_name}-graal-{unique_id}  --docker {DOCKER_GRAAL}:{function_name} -c {concurrency} -m {memory}'
    output = execute(cmd)
    print(output)


def delete(function_name, unique_id, main):
    if main:
        fn = f'{function_name}-photon-{unique_id}'
    else:
        fn = f'{function_name}-graal-{unique_id}'

    cmd = f'wsk --apihost https://{ip_address} ' \
          f'--auth 23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP ' \
          f'action delete -i {fn}'
    output = execute(cmd)
    print(output)


def invoke(function_name, payload):
    request_url = url % function_name

    r = requests.post(request_url, data=json.dumps(payload), headers=headers, verify=False)
    json_response = r.json()

    print(json_response)

    annotations = json_response['annotations']
    wait_time = 0
    init_time = 0
    duration = json_response['duration']

    for a in annotations:
        if a['key'] == 'waitTime':
            wait_time = a['value']

        if a['key'] == 'initTime':
            init_time = a['value']
            cs.set(init_time)
            cold_start_counter.inc()
        else:
            cs.set(-50)

    total_time = wait_time + init_time + duration

    exec_duration.set(total_time)

    push_to_gateway('146.193.41.231:9092', job=function_name, registry=global_registry)


def execute(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    return result.stdout
