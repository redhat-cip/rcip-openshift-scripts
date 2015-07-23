#!/bin/sh
set -e

ORIG=$(cd $(dirname $0); pwd)

eval $(${ORIG}/get_env.py)
ETCD="etcdctl --cert-file ${etcd_certFile} --key-file ${etcd_keyFile} --ca-file ${etcd_ca} --no-sync --peers ${etcd_url}"

$ETCD ls --recursive

backupdir="${ORIG}/$(date +%Y%m%d%H%M).etcd"
mkdir -p $backupdir
echo "backuping the data directory to $backupdir"
$ETCD backup --data-dir $etcd_storage --backup-dir $backupdir
echo
du -ksh $backupdir
find $backupdir
