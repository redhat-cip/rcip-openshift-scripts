#!/bin/bash

# ========================================================================================
# ARP incomplete check for Nagios/Sensu
# =========================================================================================

# Paths to commands used in this script
PATH=$PATH:/usr/sbin:/usr/bin

# Nagios return codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

# Plugin variable description
PROGNAME=$(basename $0)
PROGPATH=$(echo $0 | sed -e 's,[\\/][^\\/][^\\/]*$,,')
VERSION="1.1"
AUTHOR="(c) 2015 Florian Lambert (flambert@redhat.com)"

# Functions plugin usage
print_version() {
    echo "$PROGNAME $VERSION $AUTHOR"
}

print_usage() {
    echo "Usage: $PROGNAME -i"
    echo
    echo "-h                  Show this page"
    echo "-v                  Script version"
    echo "-i|--incomplete     check if we have incomplete ARP"
    echo "-t|--token TOKEN    token of the service account to list IPs of pods"
    echo "                    If this option if used, CRITICAL is raised only when IPs in arp incomplete state match IP of a pod."
}

print_help() {
    print_version
    echo
    print_usage
    echo
    exit 0
}

# check the number of incomplete ARP (legacy)
check_incomplete() {
    ARP_INCOMPLETE=`arp -a | grep incomplete | wc -l`
    if [ "$ARP_INCOMPLETE" -gt "0" ]; then
        echo "ARP CRITICAL : ${ARP_INCOMPLETE} incomplete"
        exit $STATE_CRITICAL
    else
        echo "ARP OK : 0 incomplete"
        exit $STATE_OK
    fi
}

# check the number of incomplete ARP that match IP of running pods
check_incomplete_with_token() {
    oc login --token="$1" > /dev/null
    local tmp=$(mktemp)
    oc get pods --all-namespaces --template='{{range .items}}{{.status.podIP}}{{"\n"}}{{end}}' |sed 's/^/^/;s/$/$/;s/\./\\./g' >> $tmp
    local match=$(arp | grep incomplete | awk '{print $1}' | grep -f $tmp | tr '\n' ' ')
    rm $tmp

    if [ -z "$match" ]; then
        echo "ARP OK : 0 incomplete"
        exit $STATE_OK
    else
        echo "ARP CRITICAL : incomplete found: ${match}"
        exit $STATE_CRITICAL
    fi
}

# -------------------------------------------------------------------------------------
# Grab the command line arguments
# -------------------------------------------------------------------------------------
while [ $# -gt 0 ]; do
    case "$1" in
        -h | --help)
            print_help
            exit $STATE_OK
            ;;
        -v | --version)
            print_version
            exit $STATE_OK
            ;;
        -t | --token)
            TOKEN=$2
            shift
            ;;
        -i | --incomplete)
            CHECK=yes
            ;;
        *)
            echo "Unknown argument: $1"
            print_usage
            exit $STATE_UNKNOWN
            ;;
    esac
    shift
done

if [ "$CHECK" = "yes" ]; then
    if [ -z "$TOKEN" ]; then
        check_incomplete
    else
        check_incomplete_with_token "$TOKEN"
    fi
fi
