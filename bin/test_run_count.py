#!/usr/bin/python3
import csv
import datetime
import os
import requests
import requests_cache
import sys

sys.path.append(os.path.join(sys.path[0], "../", "lib"))
import squad_client

test_runs_by_date = []

def squad_datetime_to_YYYYMMDDHH(time_s):
    return datetime.datetime.strptime(time_s, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d%H")


requests_cache.install_cache('qa_reports')

build_urls = {
    'mainline': "https://qa-reports.linaro.org/api/projects/22/builds/",
    '4.9': "https://qa-reports.linaro.org/api/projects/23/builds/",
}
for branch, build_url in build_urls.items():
    builds = squad_client.Builds(build_url)
    for build in builds:
        if not build.get('finished', False):
            # Only consider finished builds
            continue
        print(build['status'])
        result = requests.get(build['status'])
        result.raise_for_status()
        status = result.json()
        test_count = status['tests_pass']+status['tests_fail']
        if test_count < 100:
            # Disregard outliers
            continue
        test_runs_by_date.append(
            [
                build['id'],
                branch,
                build['version'],
                squad_datetime_to_YYYYMMDDHH(build['datetime']),
                test_count,
            ]
        )
        #test_runs_by_date[build['datetime']] = status['tests_pass']+status['tests_fail']

with open("test_run_count.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(['build_id', 'branch', 'version', 'datetime', 'test_count'])
    writer.writerows(test_runs_by_date)
