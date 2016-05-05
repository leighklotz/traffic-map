#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

JSON_OUTPUT=${OUTPUT}/security-groups-${YMD}.json

cd ${DIR}

echo "$0: visualizing ec2 security groups to $JSON_OUTPUT"
export PYTHONPATH=${PYTHONPATH}:${DIR}/..
python extract-by-reference.py ${COMPRESSED_SECURITY_GROUPS} > ${JSON_OUTPUT}
