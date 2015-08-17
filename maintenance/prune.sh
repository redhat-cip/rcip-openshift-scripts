#!/bin/bash
# -*- coding: utf-8 -*-
# Author: Florian Lambert <flambert@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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
    echo "$(datenow) docker_prune cleanup-stopped-pods.py" >> $LOGFILE
    for i in $(python /opt/rcip-openshift-scripts/maintenance/cleanup-stopped-pods.py);do
        echo "   rm $i" >> $LOGFILE
        /usr/bin/docker rm $i 2>&1 >> $LOGFILE
    done
}


function docker_prune_images {
    echo "$(datenow) docker_prune_images" >> $LOGFILE
    for i in $(/usr/bin/docker images -q);do
        echo "   rmi $i" >> $LOGFILE
        /usr/bin/docker rmi $i 2>&1 >> $LOGFILE
    done
}

case "$1" in
    openshift)
        openshift_prune
        ;;
    docker)
        docker_prune
        ;;
    docker-images)
        docker_prune_images
        ;;
    all)
        openshift_prune
		docker_prune
        docker_prune_images
        ;;
    *)
        echo  "Usage: $0 {openshift|docker|all}"
        exit 1
        ;;
esac

exit 0

