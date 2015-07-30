#!/bin/bash

LOGFILE='/tmp/prune.log'

function datenow {
    echo $(/usr/bin/date +%Y-%m-%d-%Hh%Mm%S)
}

echo "$(datenow) prune builds" >> $LOGFILE
/usr/bin/oadm prune builds --confirm  2>&1 >> $LOGFILE
echo "$(datenow) prune deployments" >> $LOGFILE
/usr/bin/oadm prune deployments --confirm  2>&1 >> $LOGFILE
#echo "$(datenow) prune images" >> $LOGFILE
#/usr/bin/oadm prune images --confirm  2>&1 >> $LOGFILE
