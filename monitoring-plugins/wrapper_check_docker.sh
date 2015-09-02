#!/bin/sh

timeout 5 /opt/check_docker/check_docker --base-url='unix:///var/run/docker.sock' --crit-data-space=90 --warn-data-space=85 --crit-meta-space=90 --warn-meta-space=85
R=$?
if [ "$?" = '124' ]; then
  echo "CRITICAL docker timeout"
  exit 2
fi

exit $R
