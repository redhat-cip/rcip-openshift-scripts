#!/bin/sh

timeout 5 /opt/check_docker/check_docker $@
R=$?
if [ "$R" = '124' ]; then
  echo "CRITICAL docker timeout"
  exit 2
fi

exit $R
