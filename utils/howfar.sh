#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

if [ ! -d ${DATDIR} ]; then
  echo "Not started"
elif ls ${DATDIR}/host*.dat.gz 1> /dev/null 2>&1; then
  echo "Completed"
elif ls ${DATDIR}/host*.dat 1> /dev/null 2>&1; then
  echo "Running"
elif [ -e ${DATDIR}/ips.txt ] ; then
  echo "Starting"
else 
  echo $((`ls ${DATDIR}/host*.dat | wc -l` *100 / ` cat ${DATDIR}/ips.txt | wc -l`))%
fi
