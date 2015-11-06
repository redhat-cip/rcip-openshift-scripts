#!/bin/sh
set -e

BACKUPDIR='/opt/backup/etcd'

ORIG=$(cd $(dirname $0); pwd)

eval $(${ORIG}/get_env.py)


mkdir -p "${BACKUPDIR}/cold_backup"
colddir="${BACKUPDIR}/cold_backup/$(date +%Y%m%d%H%M).etcd"

if [ "$etcd_outside_openshift" = "yes" ]; then
	systemctl stop etcd
else
	systemctl stop openshift-master
fi

cp -r $etcd_storage $colddir

if [ "$etcd_outside_openshift" = "yes" ]; then
	systemctl start etcd
else
	systemctl start openshift-master
fi
