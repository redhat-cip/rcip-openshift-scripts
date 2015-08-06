#!/bin/sh
set -e

ORIG=$(cd $(dirname $0); pwd)

eval $(${ORIG}/get_env.py)


mkdir -p "${ORIG}/cold_backup"
backupdir="${ORIG}/cold_backup/$(date +%Y%m%d%H%M).etcd"

systemctl stop openshift-master
cp -r $etcd_storage $backupdir
systemctl start openshift-master
