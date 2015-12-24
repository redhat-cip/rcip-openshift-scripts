#!/usr/bin/env python

import yaml
import re
import sys
import os

if len(sys.argv) == 2:
    basedir = sys.argv[1]
else:
    basedir = '/etc/openshift/master'

with open(os.path.join(basedir, 'master-config.yaml'), 'r') as stream:
    conf = yaml.load(stream)
    clientconf = conf['etcdClientInfo']
    print('export etcd_ca=' + os.path.join(basedir, clientconf['ca']))
    print('export etcd_certFile=' + os.path.join(basedir, clientconf['certFile']))
    print('export etcd_keyFile=' + os.path.join(basedir, clientconf['keyFile']))
    print('export etcd_url=' + ','.join(clientconf['urls']))
    try:
        stor = conf['etcdConfig']['storageDirectory']
    except:
        for line in open('/etc/etcd/etcd.conf', 'r'):
            if re.search('ETCD_DATA_DIR', line):
                stor = line.replace('ETCD_DATA_DIR=', '').rstrip('\n/')
                print('export etcd_outside_openshift=yes')
                break
    print('export etcd_storage=%s' % stor)
