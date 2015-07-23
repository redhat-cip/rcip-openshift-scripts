#!/usr/bin/env python

import yaml
basedir='/etc/openshift/master/'

with open(basedir + 'master-config.yaml', 'r') as stream:
    conf = yaml.load(stream)
    clientconf = conf['etcdClientInfo']
    print('export etcd_ca=' + basedir + clientconf['ca'])
    print('export etcd_certFile=' + basedir + clientconf['certFile'])
    print('export etcd_keyFile=' + basedir + clientconf['keyFile'])
    print('export etcd_url=' + clientconf['urls'][0])
    print('export etcd_storage=' + conf['etcdConfig']['storageDirectory'])
