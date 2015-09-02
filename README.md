# rcip-openshift-scripts



##monitoring-plugins/check_openshift.py

Use token to request openshift api (/api/v1beta3/)  with Oauth.
If you didn't have token, use user/pass to perform an "oc login" and get a token.

3 checks are available
  * check_nodes : Request status of nodes through openshift API
  * check_pods : Request status of pods (with deployconfig : docker-registry and router)
  * check_regions : Request regions affected on nodes and return warning if it's  match to your "OFFLINE" region

Script help

```bash
python check_openshift.py -h
usage: check_openshift.py [-h] [-proto PROTOCOL] [-H HOST] [-P PORT]
                          [-u USERNAME] [-p PASSWORD] [-t TOKEN]
                          [--check_nodes] [--check_pods] [--check_regions]
                          [--region_offline REGION_OFFLINE]

Openshift check pods

optional arguments:
  -h, --help            show this help message and exit
  -proto PROTOCOL, --protocol PROTOCOL
                        Protocol openshift (Default : https)
  -H HOST, --host HOST  Host openshift (Default : 127.0.0.1)
  -P PORT, --port PORT  Port openshift (Default : 8443)
  -u USERNAME, --username USERNAME
                        Username openshift (ex : sensu)
  -p PASSWORD, --password PASSWORD
                        Password openshift
  -t TOKEN, --token TOKEN
                        Token openshift (use token or user/pass
  --check_nodes         Check status of all nodes
  --check_pods          Check status of pods ose-haproxy-router and ose-
                        docker-registry
  --check_regions       Check if your nodes are in your "OFFLINE" region. Only
                        warning (define by --region_offline)
  --region_offline REGION_OFFLINE
                        Your "OFFLINE" region name (Default: OFFLINE)
  -v, --version         Print script version
```

We suggest to use a permanant token from a ServiceAccount. Exemple on how create one


```bash
echo '{
  "apiVersion": "v1",
  "kind": "ServiceAccount",
  "metadata": {
    "name": "metrics"
  }
}' > metricsSA.json
 
oc create -f metricsSA.json

oc describe serviceaccount metrics
oc describe secret metrics-token-bsd4v

oadm policy add-cluster-role-to-user cluster-reader system:serviceaccount:default:metrics
```
