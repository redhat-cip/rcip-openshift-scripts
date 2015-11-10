#!/bin/sh
set -e

BACKUPDIR='/opt/backup/etcd'

ORIG=$(cd $(dirname $0); pwd)

eval $(${ORIG}/get_env.py)

# try to contact etcd before doing anything
ETCDCTL="etcdctl --cert-file ${etcd_certFile} --key-file ${etcd_keyFile} --ca-file ${etcd_ca} --no-sync --peers ${etcd_url}"
$ETCDCTL ls

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
