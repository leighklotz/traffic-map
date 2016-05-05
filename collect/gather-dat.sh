#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

# Gather traffic data from hosts, unless we already have it for the day.

DAT=${DATDIR}/all.dat

if [ -f ${DAT}.gz ]
then
   echo "$0: Uncompressing existing ${DAT}.gz"
   gunzip ${DAT}.gz
fi

if [ ! -f ${DAT} ]
then

 echo -n "sudo password: "
 read -s sudo_password
 echo ""

 HOSTS=`cat ${HOSTS_TXT}`
 echo "$0: Collection of hosts determined:"
 echo $HOSTS

 COMMAHOSTS=`echo $HOSTS|sed -e 's/ /,/g'`

 echo "$0: Collecting TCP traffic from those IPs"
 # pass in password on stdin without having it show up in process list
 fab --hosts=$COMMAHOSTS --set DATDIR=${DATDIR} capture_packets <<< "$sudo_password"

 echo "$0: Producing single traffic file ${DAT}"
 cat ${DATDIR}/host-*.dat > ${DAT}
 gzip ${DATDIR}/host-*.dat
fi
