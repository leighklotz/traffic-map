#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

# Gather loadavg, uptime, and free

HOSTS=`cat ${HOSTS_TXT}`
echo "$0: Collection of hosts determined:"
echo $HOSTS

COMMAHOSTS=`echo $HOSTS|sed -e 's/ /,/g'`

echo "$0: Collecting Uptime and load average"
echo -n "password: "
fab --hosts=$COMMAHOSTS --set DATDIR=${DATDIR} get_uptime_load

