import json
import subprocess

import requests as requests
import urllib3
from prometheus_client import CollectorRegistry, Counter, push_to_gateway, Histogram
import numpy as np

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

counters = {}
timers = {}

BUCKETS = np.concatenate((np.arange(0., 100., 10.),
                          np.arange(120., 500., 20.),
                          np.arange(550., 2000., 50.),
                          np.arange(2100., 5000., 100.),
                          np.arange(5200., 30000., 500.))).tolist()

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
        fn = f'{function_name}-{unique_id}-hotspot'
    else:
        fn = f'{function_name}-{unique_id}-graal'

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
            cs = __get_or_insert(timers, function_name + "-cs",
                                 lambda: Histogram('cold_start_time', 'Cold start time', buckets=BUCKETS, registry=coldstart_registry))
            cs.observe(init_time)
            push_to_gateway('146.193.41.231:9092', job=function_name + "-cold-starts", registry=coldstart_registry)
            cold_start_counter = __get_or_insert(counters, function_name + "-cs",
                                                 lambda: Counter('cold_start_counter', 'Cold start counter',
                                                                 registry=global_registry))
            cold_start_counter.inc()

    total_time = wait_time + init_time + duration

    exec_duration = __get_or_insert(timers, function_name + "-ed",
                                    lambda: Histogram('function_execution_time', 'Execution time', buckets=BUCKETS,
                                                      registry=global_registry))
    exec_duration.observe(total_time)
    exec_duration_counter = __get_or_insert(counters, function_name + "-ed",
                                            lambda: Counter('function_execution_count', 'Execution counter',
                                                            registry=global_registry))
    exec_duration_counter.inc()

    push_to_gateway('146.193.41.231:9092', job=function_name, registry=global_registry)


def __get_or_insert(d: dict, key, lazy_value):
    if key not in d:
        d[key] = lazy_value()
    return d[key]


def execute(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    return result.stdout
