#!/usr/bin/env python

import yaml
import re
basedir='/etc/openshift/master/'

with open(basedir + 'master-config.yaml', 'r') as stream:
    conf = yaml.load(stream)
    clientconf = conf['etcdClientInfo']
    print('export etcd_ca=' + basedir + clientconf['ca'])
    print('export etcd_certFile=' + basedir + clientconf['certFile'])
    print('export etcd_keyFile=' + basedir + clientconf['keyFile'])
    print('export etcd_url=' + clientconf['urls'][0])
    try:
        stor = conf['etcdConfig']['storageDirectory']
    except:
        for line in open('/etc/etcd/etcd.conf', 'r'):
            if re.search('ETCD_DATA_DIR', line):
                stor = line.replace('ETCD_DATA_DIR=', '').rstrip()
                break
    print('export etcd_storage=%s' % stor)
