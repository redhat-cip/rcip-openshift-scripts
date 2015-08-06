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
systemctl start openshift-master
