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
if [ "$etcd_outside_openshift" = "yes" ]; then
	systemctl stop etcd
fi
mv "${etcd_storage}" "${etcd_storage}.$(date +%Y%m%d%H%M).bak"
etcdpermission=$(stat -c '%U:%G' ${etcd_storage})
cp -r $backupdir $etcd_storage
chown -R $etcdpermission ${etcd_storage}
etcd_log=$(mktemp)
tail -f $etcd_log | if grep -q 'etcdserver: published'; then pkill etcd ; fi&
set +e
etcd --data-dir=$etcd_storage --force-new-cluster |& tee -a $etcd_log
set -e
rm $etcd_log
if [ "$etcd_outside_openshift" = "yes" ]; then
	systemctl start etcd
fi
systemctl start openshift-master
