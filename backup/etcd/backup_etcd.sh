#!/bin/sh
set -e

# env variables you may want to change
BACKUPDIR=${BACKUPDIR:-"/opt/backup/etcd"}

hotdir="${BACKUPDIR}/hot/$(date +%Y%m%d%H%M).etcd"
mkdir -p $hotdir

. /etc/etcd/etcd.conf

echo "backuping the data directory to $hotdir"
etcdctl backup --data-dir ${ETCD_DATA_DIR} --backup-dir $hotdir
if [[ -e ${ETCD_DATA_DIR}/member/snap/db ]]; then
    cp -a ${ETCD_DATA_DIR}/member/snap/db ${hotdir}/member/snap/
fi
echo
du -ksh $hotdir
find $hotdir
