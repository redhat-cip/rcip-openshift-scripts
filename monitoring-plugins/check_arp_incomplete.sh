#!/bin/bash

# ========================================================================================
# ARP incomplete check for Nagios/Sensu
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
	echo "-i --incomplete check if we have incomplete ARP"
}

print_help() {
	print_version
	echo ""
	print_usage
        echo ""
	exit 0
}

check_incomplete() {
  #check the number of incomplete ARP
  ARP_INCOMPLETE=`arp -a | grep incomplete | wc -l`
  if [ "$ARP_INCOMPLETE" -gt "0" ]; then
    echo "ARP CRITICAL : ${ARP_INCOMPLETE} incomplete"
    exit $STATE_CRITICAL
  else 
  	echo "ARP OK : 0 incomplete"
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
		-i | --incomplete)
		check_incomplete
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

