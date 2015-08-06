#!/bin/bash
set -e

# minimum number of backup to keep
KEEP=20

ORIG=$(cd $(dirname $0); pwd)

for d in . cold_backup; do
    ls -d $ORIG/$d/*.etcd | head -n "-${KEEP}" | while read i; do
      [ ! -z "$i" ] && [ -d $i ] && [[ $i =~ .etcd ]] && rm -rf $i
    done
done
