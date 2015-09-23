#!/bin/sh

timeout 5 /etc/sensu/plugins/check_docker $@
R=$?
if [ "$R" = '124' ]; then
  echo "CRITICAL docker timeout"
  exit 2
fi

exit $R
