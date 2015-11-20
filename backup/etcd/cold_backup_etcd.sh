#!/bin/sh
set -e

ORIG=$(cd $(dirname $0); pwd)

# env variables you may want to change
BACKUPDIR=${BACKUPDIR:-"/opt/backup/etcd"}
DAEMON_NAME=${DAEMON_NAME:-"openshift-master"}
MASTER_CONF=${MASTER_CONF:-"/etc/openshift/master"}

eval $(${ORIG}/get_env.py "${MASTER_CONF}")

# try to contact etcd before doing anything
ETCDCTL="etcdctl --cert-file ${etcd_certFile} --key-file ${etcd_keyFile} --ca-file ${etcd_ca} --no-sync --peers ${etcd_url}"
$ETCDCTL ls

mkdir -p "${BACKUPDIR}/cold_backup"
colddir="${BACKUPDIR}/cold_backup/$(date +%Y%m%d%H%M).etcd"

if [ "$etcd_outside_openshift" = "yes" ]; then
  systemctl stop etcd
else
  systemctl stop ${DAEMON_NAME}
fi

cp -r $etcd_storage $colddir

if [ "$etcd_outside_openshift" = "yes" ]; then
  systemctl start etcd
else
  systemctl start ${DAEMON_NAME}
fi
