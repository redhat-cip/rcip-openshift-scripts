#!/bin/sh
HOSTNAME="${COLLECTD_HOSTNAME:-localhost}"
INTERVAL="${COLLECTD_INTERVAL:-60}"

TOKEN=$(cat $1)
API_URL='/api/v1beta3'

nodes=$(curl -s --insecure --header "Authorization: Bearer $TOKEN" https://127.0.0.1:8443$API_URL/nodes |/opt/bin/jq -r '.items[] | .metadata.name')

while sleep "$INTERVAL"; do
  VALUE=$(curl -s --insecure --header "Authorization: Bearer $TOKEN" https://127.0.0.1:8443$API_URL/pods \
         |/opt/bin/jq '.items[] | select(.status.phase == "Running") | .metadata.name' \
         |wc -l) 
  echo "PUTVAL \"$HOSTNAME/openshift/gauge-pods_count_total\" interval=$INTERVAL N:$VALUE"
  for node in $nodes; do
    VALUE=$(curl -s --insecure --header "Authorization: Bearer $TOKEN" https://127.0.0.1:8443$API_URL/pods \
            |/opt/bin/jq ".items[] | select(.status.phase == \"Running\") | select(.spec.host == \"${node}\") | .metadata.name" \
            |wc -l)
    echo "PUTVAL \"$HOSTNAME/openshift/gauge-pods_count_${node}\" interval=$INTERVAL N:$VALUE"
  done
done
