#!/bin/bash
set -e

# minimum number of backup to keep
KEEP=20

ORIG=$(cd $(dirname $0); pwd)

ls -d $ORIG/*.etcd | head -n "-${KEEP}" | while read i; do
  [ ! -z "$i" ] && [ -d $i ] && [[ $i =~ .etcd ]] && rm -rf $i
done
