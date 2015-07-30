#!/bin/bash

#crontab : */30 * * * * bash /opt/rcip-openshift-scripts/maintenance/prune.sh all

LOGFILE='/tmp/prune.log'

function datenow {
    echo $(/usr/bin/date +%Y-%m-%d-%Hh%Mm%S)
}

function openshift_prune {
	echo "$(datenow) openshift-prune builds" >> $LOGFILE
	/usr/bin/oadm prune builds --confirm  2>&1 >> $LOGFILE
	echo "$(datenow) openshift-prune deployments" >> $LOGFILE
	/usr/bin/oadm prune deployments --confirm  2>&1 >> $LOGFILE
	#echo "$(datenow) openshift-prune images" >> $LOGFILE
	#/usr/bin/oadm prune images --confirm  2>&1 >> $LOGFILE
}

function docker_prune {
    echo "$(datenow) cleanup-stopped-pods.py" >> $LOGFILE
    for i in $(python /opt/rcip-openshift-scripts/maintenance/cleanup-stopped-pods.py);do
        echo "   rm $i" >> $LOGFILE
        /usr/bin/docker rm $i 2>&1 >> $LOGFILE
    done
}

case "$1" in
    openshift)
        openshift_prune
        ;;
    docker)
        docker_prune
        ;;
    all)
        openshift_prune
		docker_prune
        ;;
    *)
        echo  "Usage: $0 {openshift|docker|all}"
        exit 1
        ;;
esac

exit 0

