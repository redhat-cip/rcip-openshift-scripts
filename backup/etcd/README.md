For example, on the master :

    yum install -y etcd
    git clone https://github.com/redhat-cip/rcip-openshift-scripts.git /opt/rcip-openshift-scripts
    cp /opt/rcip-openshift-scripts/backup/etcd/logrotate /etc/logrotate.d/backup_etcd
    crontab -e
    0 */12 * * * /opt/rcip-openshift-scripts/backup/etcd/backup_etcd.sh >> /var/log/backup_etcd.log
    1 */12 * * * /opt/rcip-openshift-scripts/backup/etcd/purge.sh >> /var/log/purge_backup_etcd.log

