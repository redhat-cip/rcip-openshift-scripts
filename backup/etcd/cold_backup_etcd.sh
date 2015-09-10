#!/bin/sh
set -e

BACKUPDIR='/opt/backup/etcd'

ORIG=$(cd $(dirname $0); pwd)

eval $(${ORIG}/get_env.py)


mkdir -p "${BACKUPDIR}/cold_backup"
colddir="${BACKUPDIR}/cold_backup/$(date +%Y%m%d%H%M).etcd"

systemctl stop openshift-master
cp -r $etcd_storage $colddir
systemctl start openshift-master
