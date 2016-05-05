#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo "$0: List IPs to ${IPS}"

if [ !  -f ${IPS} ]; then
  echo "$0: Getting list of IPs"
  export PYTHONPATH=${PYTHONPATH}:${DIR}/..
  ./list-ec2-hosts-table.py > ${IPS}
fi

echo "$0: Created ${IPS}"

