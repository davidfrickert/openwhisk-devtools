#!/bin/bash
## Run this to apply correct permissions to mounted folders
chown -R 472:root grafana grafana_data
chown -R nobody:nogroup prometheus_prometheus_data
