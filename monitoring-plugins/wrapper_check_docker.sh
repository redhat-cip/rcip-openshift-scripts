#!/bin/sh

#$1 check_docker path (ex: /etc/sensu/plugins/check_docker)
#$@ all check_docker params
CHECK_DOCKER=$1
shift

timeout 5 $CHECK_DOCKER $@
R=$?
if [ "$R" = '124' ]; then
  echo "CRITICAL docker timeout"
  exit 2
fi

exit $R
