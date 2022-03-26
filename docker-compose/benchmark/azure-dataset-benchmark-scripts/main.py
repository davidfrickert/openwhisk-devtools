#!/usr/bin/python3
import csv
import time
from argparse import ArgumentParser
from time import sleep
import ow

parser = ArgumentParser()

parser.add_argument("--memory-min", type=int, dest='mem_min', required=True, help="Memory min")
parser.add_argument("--memory-max", type=int, dest='mem_max', required=True, help="Memory max")
parser.add_argument("-f", "--function", type=str, dest='function', help="Function Name (openwhisk)")

args = parser.parse_args()

FOLDER = 'azurefunctions-dataset2019/'

MEMORY = FOLDER + 'app_memory_percentiles.anon.d{:02d}.csv'
FUNCTION_DURATION = FOLDER + 'function_durations_percentiles.anon.d{:02d}.csv'
INVOCATIONS = FOLDER + 'invocations_per_function_md.anon.d{:02d}.csv'


def find_suitable_function(excluded_apps=None):
    if excluded_apps is None:
        excluded_apps = []
    best_match = None
    print('searching suitable functions')
    for i in range(1, 13):
        current_file = MEMORY.format(i)
        csv_reader = csv.DictReader(open(current_file))
        for row in csv_reader:
            app = row['HashApp']
            avg_mem = int(row['AverageAllocatedMb'])
            max_mem = int(row['AverageAllocatedMb_pct99'])
            match = (abs(args.mem_min - avg_mem) + abs(args.mem_max - max_mem))

            if (not best_match or match < best_match) and app not in excluded_apps:
                best_match = match
                best_avg_mem = avg_mem
                best_max_mem = max_mem
                best_app = app
                best_row = row
                best_file_n = i
    print(
        f'App with most similar memory usage: {best_app}, with average memory {best_avg_mem} and maximum memory {best_max_mem}')
    # print(best_row)
    return {'index': best_file_n, 'app': best_app}


success = False
excluded = []

while not success:
    result = find_suitable_function(excluded)

    current_file = INVOCATIONS.format(result['index'])
    csv_reader = csv.DictReader(open(current_file))
    print('searching for invocations')
    for row in csv_reader:
        if row['HashApp'] == result['app']:
            n_invocations_in_24h = 0
            for i in range(1, 1441):
                n_invocations_in_24h += int(row[str(i)])
            print(f'Usages in 24h - {n_invocations_in_24h}')
            if n_invocations_in_24h > 300:
                success = True
                # print(row)
                invocations = row
            else:
                excluded.append(result['app'])
            break

print("Starting benchmark")

for i in range(1, 1441):
    invocations_current_minute = int(invocations[str(i)])
    now = time.time()

    print(f"Invocations for current minute: {invocations_current_minute}")
    if invocations_current_minute == 0:
        sleep(60)
    else:
        t = 60 / invocations_current_minute
        for _ in range(invocations_current_minute):
            b_invoke = time.time()
            ow.send(args.function, {"time": 1000})
            invoke_elapsed = time.time() - b_invoke
            if t - invoke_elapsed > 0:
                sleep(t - invoke_elapsed)
