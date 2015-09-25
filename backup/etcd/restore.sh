#!/bin/bash
set -e

ORIG=$(cd $(dirname $0); pwd)

eval $(${ORIG}/get_env.py)

backupdir=$1

if [ -z "$backupdir" ] || [ ! -d "$backupdir" ] || [[ ! $backupdir =~ .etcd ]]; then
  echo "'${backupdir}' is not a proper etcd datadir"
  echo
  echo "Usage: $0 backupdir   # where backupdir is the etcd datadir to restore"
  exit 2
fi

systemctl stop openshift-master
mv "${etcd_storage}" "${etcd_storage}.$(date +%Y%m%d%H%M).bak"
cp -r $backupdir $etcd_storage
etcd_log=$(mktemp)
tail -f $etcd_log | if grep -q 'etcdserver: published'; then pkill etcd ; fi&
set +e
etcd --data-dir=$etcd_storage --force-new-cluster |& tee -a $etcd_log
set -e
rm $etcd_log
systemctl start openshift-master
