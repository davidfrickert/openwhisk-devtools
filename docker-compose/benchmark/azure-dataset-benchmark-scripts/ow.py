import json
import subprocess

import requests as requests
import urllib3
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway

DOCKER_GRAAL = 'davidfrickert/openwhisk-runtime-nativeimage-basefunction'
DOCKER_OPENJ9 = 'davidfrickert/photon:hotspot'

ip_address = '146.193.41.200'
url = f'https://{ip_address}/api/v1/namespaces/_/actions/%s?blocking=true&result=false'
headers = {
    "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=",
    "Content-Type": "application/json",
    "User-Agent": "OpenWhisk-CLI/1.0 (2019-08-10T00:47:48.313+0000) linux amd64"
}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

global_registries = {}
coldstart_registries = {}

cold_start_counters = {}
cold_start_timers = {}
exec_durations = {}

def create(function_name, concurrency, memory, docker_tag, main):
    if main:
        cmd = f'wsk --apihost https://{ip_address} ' \
              f'--auth 23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP ' \
              f'action create -i {function_name} jars/{docker_tag}.jar --main {main} --docker {DOCKER_OPENJ9} -c {concurrency} -m {memory}'
    else:
        cmd = f'wsk --apihost https://{ip_address} ' \
              f'--auth 23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP ' \
              f'action create -i {function_name} --docker {DOCKER_GRAAL}:{docker_tag} -c {concurrency} -m {memory}'
    output = execute(cmd)
    print(output)


def delete(function_name, unique_id, main):
    if main:
        fn = f'{function_name}-hotspot-{unique_id}'
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

    global_registry = __get_or_insert(global_registries, function_name, lambda: CollectorRegistry())

    for a in annotations:
        if a['key'] == 'waitTime':
            wait_time = a['value']

        if a['key'] == 'initTime':
            init_time = a['value']
            coldstart_registry = __get_or_insert(coldstart_registries, function_name, lambda: CollectorRegistry())
            cs = __get_or_insert(cold_start_timers, function_name, lambda: Gauge('cold_start_time', 'Cold start time', registry=coldstart_registry))
            cs.set(init_time)
            push_to_gateway('146.193.41.231:9092', job=function_name, registry=coldstart_registry)
            cold_start_counter = __get_or_insert(cold_start_counters, function_name, lambda: Counter('cold_start_counter', 'Cold start counter', registry=global_registry))
            cold_start_counter.inc()

    total_time = wait_time + init_time + duration

    exec_duration = __get_or_insert(exec_durations, function_name, lambda: Gauge('function_execution_time', 'Execution time', registry=global_registry))
    exec_duration.set(total_time)

    push_to_gateway('146.193.41.231:9092', job=function_name, registry=global_registry)


def __get_or_insert(d: dict, key, lazy_value):
    if key not in dict:
        d['key'] = lazy_value()
    return d['key']

def execute(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    return result.stdout
