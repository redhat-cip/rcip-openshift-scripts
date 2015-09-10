#!/bin/bash
set -e

BACKUPDIR='/opt/backup/etcd'

# minimum number of backup to keep
KEEP=10

for d in hot cold_backup; do
    ls -d $BACKUPDIR/$d/*.etcd | head -n "-${KEEP}" | while read i; do
      [ ! -z "$i" ] && [ -d $i ] && [[ $i =~ .etcd ]] && rm -rf $i
    done
done
