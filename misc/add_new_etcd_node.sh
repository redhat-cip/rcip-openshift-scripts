#!/bin/sh
# Author: Guillaume Coré <gucore@redhat.com>
# Description: this script adds an etcd node to an existing cluster
#
# Prerequisites: the script has to be used on an openshift platform installed with rcip
# playbook : see https://github.com/redhat-cip/rcip-openshift-ansible
# Some tests are run before doing anything to be sure required components or tools are present.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

set -e

###########
#CONF
###########
_hostname=$1
_ip=$2

########### </CONF>

node="${_hostname}"
dir=$(mktemp -d)
# use by openssl as subjectAltName  (see /etc/etcd/ca/openssl.cnf)
export SAN="IP:${_ip}"

###########
# TESTS
###########

if [ -z "${_ip}" ] || [ -z "$node" ]; then
  echo "usage $0 HOSTNAME IP" >&2
  exit 2
fi

echo -n "do you have a recent etcd backup ? (CTRL+C to quit, ENTER to continue)"
read

if [ ! -d /etc/etcd/ca ]; then
  echo "you need the ca folder from the first etcd used by the playbook openshift-ansible to sign to sign other certs" >&2
  exit 2
fi


. /root/.etcd.bashrc
if [ -z "$ETCDCTL" ]; then
  echo '$ETCDCTL alias not present (check /root/.etcd.bashrc)' >&2
  exit 2
fi

$ETCDCTL cluster-health

if $ETCDCTL cluster-health | grep unhealthy; then
  echo 'one etcd node is unhealthy, please fix first' >&2
  exit 2
fi


echo "try to reach ${node}"
ping -c1 ${_ip}
ssh ${node} hostname
ssh ${_ip} hostname
[ "$(ssh ${node} hostname)" = "$(ssh ${_ip} hostname)" ]

if ssh ${node} pgrep -f /usr/bin/etcd; then
  echo "running etcd process found on ${node}, leaving." >&2
  exit 2
fi
if ssh ${node} [ -f /etc/etcd/server.key ]; then
  echo "certificates already exist on ${node}, remove them if you want to regenerate new ones." >&2
  exit 2
fi
if ! ssh ${node} which etcd; then
  echo "etcd must be installed on ${node}" >&2
  exit 2
fi

########### </TESTS>

mkdir -p $dir

openssl req -new -keyout ${dir}/server.key \
		 -config /etc/etcd/ca/openssl.cnf \
		 -out ${dir}/server.csr \
		 -reqexts etcd_v3_req \
		 -batch -nodes \
		 -subj  /CN=${node}

openssl ca -name etcd_ca \
		-config /etc/etcd/ca/openssl.cnf \
		-out ${dir}/server.crt\
		-in ${dir}/server.csr\
		-extensions etcd_v3_ca_server -batch

openssl req -new -keyout ${dir}/peer.key \
		-config /etc/etcd/ca/openssl.cnf \
		-out ${dir}/peer.csr \
		-reqexts etcd_v3_req -batch -nodes \
		-subj /CN=${node}

openssl ca -name etcd_ca \
		-config /etc/etcd/ca/openssl.cnf \
		-out ${dir}/peer.crt \
		-in ${dir}/peer.csr \
		-extensions etcd_v3_ca_peer -batch


rsync -av ${dir}/ ${node}:/etc/etcd/
scp /etc/etcd/ca.crt ${node}:/etc/etcd/
ssh ${node} touch /etc/etcd/etcd.conf
ssh ${node} chown  -R etcd:etcd /etc/etcd
ssh ${node} "chmod 600 /etc/etcd/*"
ssh ${node} chmod 700 /etc/etcd
ssh ${node} 'semanage fcontext --add -t etc_t "/etc/etcd(/.*)?"'
ssh ${node} restorecon -R -v  /etc/etcd

$ETCDCTL cluster-health
$ETCDCTL member list

tmpconf=$(mktemp)
cat > $tmpconf <<EOF
ETCD_DATA_DIR="/var/lib/etcd/"
ETCD_HEARTBEAT_INTERVAL=500
ETCD_ELECTION_TIMEOUT=2500
ETCD_LISTEN_PEER_URLS=https://${_ip}:2380
ETCD_LISTEN_CLIENT_URLS=https://${_ip}:2379
ETCD_INITIAL_ADVERTISE_PEER_URLS=https://${_ip}:2380
ETCD_ADVERTISE_CLIENT_URLS=https://${_ip}:2379

ETCD_CA_FILE=/etc/etcd/ca.crt
ETCD_CERT_FILE=/etc/etcd/server.crt
ETCD_KEY_FILE=/etc/etcd/server.key
ETCD_PEER_CA_FILE=/etc/etcd/ca.crt
ETCD_PEER_CERT_FILE=/etc/etcd/peer.crt
ETCD_PEER_KEY_FILE=/etc/etcd/peer.key
EOF

$ETCDCTL member add ${node} https://${_ip}:2380|egrep '^ETCD_' >> $tmpconf

scp $tmpconf ${node}:/etc/etcd/etcd.conf
ssh ${node} cp -r /var/lib/etcd /var/lib/etcd.$(date +%Y%m%d%H%M)
ssh ${node} rm -rf /var/lib/etcd/*
ssh ${node} systemctl start etcd

sleep 5
$ETCDCTL member list
$ETCDCTL cluster-health

rm $tmpconf
rm -rf $dir

echo "Don't forget to update  master-config.yaml to add the new node to clientURL"
