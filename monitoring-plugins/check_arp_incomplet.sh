#!/bin/bash

# ========================================================================================
# ARP incomplet check for Nagios/Sensu
# 
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
VERSION="1.0"
AUTHOR="(c) 2015 Florian Lambert (flambert@redhat.com)"

# Functions plugin usage
print_version() {
    echo "$PROGNAME $VERSION $AUTHOR"
}

print_usage() {
	echo "Usage: $PROGNAME -i"
	echo ""
	echo "-h Show this page"
	echo "-v Script version"
	echo "-i --incomplet check if we have incomplet ARP"
}

print_help() {
	print_version
	echo ""
	print_usage
        echo ""
	exit 0
}

check_incomplet() {
  #check the number of incomplet ARP
  ARP_INCOMPLET=`arp -a | grep incomplet | wc -l`
  if [ "$ARP_INCOMPLET" -gt "0" ]; then
    echo "ARP CRITICAL : ${ARP_INCOMPLET} incomplet"
    exit $STATE_CRITICAL
  else 
  	echo "ARP OK : 0 incomplet"
  	exit $STATE_OK
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
		-i | --incomplet)
		check_incomplet
		;;
		*)  echo "Unknown argument: $1"
            	print_usage
            	exit $STATE_UNKNOWN
            	;;
		esac
	shift
done


# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------

