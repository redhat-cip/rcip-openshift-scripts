# openshift count pod plugin

This plugin uses plugin [Exec](https://collectd.org/wiki/index.php/Plugin:Exec).

Example conf:

    root@master:/opt/collectd-plugins$ cat /etc/collectd.d/exec.conf
    LoadPlugin exec
    <Plugin exec>
      Exec "sensu" "/opt/collectd-plugins/openshift-pods.sh" "/etc/sensu/openshift_token"
    </Plugin>

(Ensure metrics serviceacount have the correct permissions)
