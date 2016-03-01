For example, on the master :

    yum install -y etcd
    git clone https://github.com/redhat-cip/rcip-openshift-scripts.git /opt/rcip-openshift-scripts
    cp /opt/rcip-openshift-scripts/backup/etcd/logrotate /etc/logrotate.d/backup_etcd
    crontab -e
    0 */12 * * * /opt/rcip-openshift-scripts/backup/etcd/backup_etcd.sh >> /var/log/backup_etcd.log
    1 */12 * * * /opt/rcip-openshift-scripts/backup/etcd/purge.sh >> /var/log/purge_backup_etcd.log

For example, if you use also the RCIP ansible [playbook](https://github.com/redhat-cip/rcip-openshift-ansible), a cronjob should be present on masters with a MASTER_CONF set depending on <code>deployment_type</code> :

    MASTER_CONF="/etc/origin/master" /opt/rcip-openshift-scripts/backup/etcd/backup_etcd.sh

To restore a hot backup, you will have to set the variables :

    DAEMON_NAME=origin-master MASTER_CONF=/etc/origin/master /opt/rcip-openshift-scripts/backup/etcd/restore.sh /opt/backup/etcd/hot/201511200900.etcd

By default, variables DAEMON_NAME, MASTER_CONF are set for OSE 3.1.x.

For more information on paths and daemon names :
https://docs.openshift.com/enterprise/3.1/release_notes/ose_3_1_release_notes.html

It depends on the version of openshift, and the HA type as well (native, failover).
