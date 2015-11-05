#!/bin/sh
set -e

BACKUPDIR='/opt/backup/etcd'

ORIG=$(cd $(dirname $0); pwd)

eval $(${ORIG}/get_env.py)


mkdir -p "${BACKUPDIR}/cold_backup"
colddir="${BACKUPDIR}/cold_backup/$(date +%Y%m%d%H%M).etcd"

systemctl stop openshift-master
if [ "$etcd_outside_openshift" = "yes" ]; then
	systemctl stop etcd
fi
cp -r $etcd_storage $colddir
if [ "$etcd_outside_openshift" = "yes" ]; then
	systemctl start etcd
fi
systemctl start openshift-master
